import hashlib
import inspect
import json
import os
import sys
import tempfile
from inspect import _empty  # type: ignore

from flask import Blueprint, jsonify, request
from flask.helpers import make_response

import beagle.datasources  # noqa: F401
import beagle.transformers  # noqa: F401
from beagle.backends.networkx import NetworkX
from beagle.common import logger
from beagle.config import Config
from beagle.datasources.base_datasource import ExternalDataSource
from beagle.datasources.json_data import JSONData
from beagle.web.api.models import Graph
from beagle.web.server import db

api = Blueprint("api", __name__, url_prefix="/api")

# Define a mapping between datasource classes to strings
DATASOURCES = {
    # Class name is used here.
    cls[1].__name__: cls[1]
    for cls in inspect.getmembers(
        sys.modules["beagle.datasources"],
        lambda cls: inspect.isclass(cls) and not inspect.isabstract(cls),
    )
}

# Define a mapping between transformer class *names* to class objects
TRANSFORMERS = {
    # Human-readable name used here.
    cls[1].__name__: cls[1]
    for cls in inspect.getmembers(
        sys.modules["beagle.transformers"],
        lambda cls: inspect.isclass(cls) and not inspect.isabstract(cls),
    )
}

BACKENDS = {
    cls[1].__name__: cls[1]
    for cls in inspect.getmembers(
        sys.modules["beagle.backends"],
        lambda cls: inspect.isclass(cls) and not inspect.isabstract(cls),
    )
}


# Generate an array containing a description of each datasource.
# This includes it's name, it's id, it's required parameters, and the transformers
# which it can send data to.
SCHEMA = {
    "datasources": [
        {
            "id": datasource.__name__,
            "name": datasource.name,
            "params": [
                {
                    "name": k,
                    "required": (v.default == _empty),
                    "default": None if v.default == _empty else v.default,
                }  # Check if there is a default value, if not, required.
                for k, v in inspect.signature(
                    datasource
                ).parameters.items()  # Gets the expected parameters
            ],
            "type": "external" if issubclass(datasource, ExternalDataSource) else "files",
            "transformers": [
                {"id": trans.__name__, "name": trans.name} for trans in datasource.transformers
            ],
        }
        for datasource in DATASOURCES.values()
    ],
    "backends": [
        {"id": backend.__name__, "name": backend.__name__} for backend in BACKENDS.values()
    ],
}


@api.route("/datasources")
def pipelines():
    """Returns a list of all available datasources, their parameters,
    names, ids, and supported transformers.

    A single entry in the array is formatted as follows:

    >>> {
        "id": str,
        "name": str,
        "params": [
            {
                "name": str,
                "required": bool,
            }
            ...
        ],
        "transformers": [
            {
                "id": str,
                "name": str
            }
        ]
        "type": "files" OR "external
    }

    If the 'type' field is set to 'files', it means that the parameters
    represent required files, if it is set to 'external' this means that the
    parameters represent string inputs.

    The main purpose of this endpoint is to allow users to query beagle
    in order to easily identify what datasource and transformer combinations
    are possible, as well as what parameters are required.

    Returns
    -------
    List[dict]
        An array of datasource specifications.
    """

    response = jsonify(SCHEMA)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@api.route("/backends")
def get_backends():
    """Returns all possible backends, their names, and their IDs.

    The array contains elements with the following structure.

    >>> {
        id: string, # class name
        name: string # Human-readable name
    }

    These map back to the __name__ attributes of Backend subclasses.

    Returns
    -------
    List[dict]
        Array of {id: string, name: string} entries.
    """
    response = jsonify(
        [{"id": backend.__name__, "name": backend.__name__} for backend in BACKENDS.values()]
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@api.route("/transformers")
def get_transformers():
    """Returns all possible transformers, their names, and their IDs.

    The array contains elements with the following structure.

    >>> {
        id: string, # class name
        name: string # Human-readable name
    }

    These map back to the __name__ and .name attributes of Transformer subclasses.

    Returns
    -------
    List[dict]
        Array of {id: string, name: string} entries.
    """

    response = jsonify(
        [{"id": trans.__name__, "name": trans.name} for trans in TRANSFORMERS.values()]
    )
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@api.route("/new", methods=["POST"])
def new():
    """Generate a new graph using the supplied DataSource, Transformer, and the parameters
    passed to the DataSource.

    At minimum, the user must supply the following form parameters:
        1. datasource
        2. transformer
        3. comment
        4. backend

    Outside of that, the user must supply at **minimum** the parameters marked by
    the datasource as required.
        * Use the /api/datasources endpoint to see which ones these are.
        * Programmatically, these are any parameters without a default value.

    Failure to supply either the minimum three or the required parameters for that datasource
    returns a 400 status code with the missing parameters in the 'message' field.

    If any part of the graph creation yields an error, a 500 HTTP code is returend with the
    python exception as a string in the 'message' field.

    If the graph is succesfully created, the user is returned a dictionary with the ID of the graph
    and the URI path to viewing it in the *beagle web interface*.

    For example:

    >>> {
        id: 1,
        self: /fireeye_hx/1
    }

    Returns
    -------
    dict
        {id: integer, self: string}
    """

    # Verify we have the basic parameters.
    missing_params = []
    for param in ["datasource", "transformer", "comment"]:
        if param not in request.form:
            missing_params.append(param)

    if len(missing_params) > 0:
        logger.debug(f"Request to /new missing parameters: {missing_params}")
        return make_response(jsonify({"message": f"Missing parameters {missing_params}"}), 400)

    # Get the
    requested_datasource = request.form["datasource"]
    requested_transformer = request.form["transformer"]
    requested_backend = request.form.get("backend", "NetworkX")

    datasource_schema = next(
        filter(lambda entry: entry["id"] == requested_datasource, SCHEMA["datasources"]), None
    )

    if datasource_schema is None:
        logger.debug(f"User requested a non-existent data source {requested_datasource}")
        return make_response(
            jsonify(
                {
                    "message": f"Requested datasource '{requested_datasource}' is invalid, "
                    + "please use /api/datasources to find a list of valid datasources"
                }
            ),
            400,
        )

    logger.info(
        f"Recieved upload request for datasource=<{requested_datasource}>, "
        + f"transformer=<{requested_transformer}>, backend=<{requested_backend}>"
    )

    datasource_cls = DATASOURCES[requested_datasource]
    transformer_cls = TRANSFORMERS[requested_transformer]
    backend_class = BACKENDS[requested_backend]

    required_parameters = datasource_schema["params"]

    # If this class extends the ExternalDataSource class, we know that the parameters
    # represent strings, and not files.
    is_external = issubclass(datasource_cls, ExternalDataSource)

    # Make sure the user provided all required parameters for the datasource.
    datasource_missing_params = []
    for param in required_parameters:
        # Skip missnig parameters
        if param["required"] is False:
            continue
        if is_external and param["name"] not in request.form:
            datasource_missing_params.append(param["name"])

        if not is_external and param["name"] not in request.files:
            datasource_missing_params.append(param["name"])

    if len(datasource_missing_params) > 0:
        logger.debug(
            f"Missing datasource {'form' if is_external else 'files'} params {datasource_missing_params}"
        )
        return make_response(
            jsonify(
                {
                    "message": f"Missing datasource {'form' if is_external else 'files'} params {datasource_missing_params}"
                }
            ),
            400,
        )

    logger.info("Transforming data to a graph.")

    logger.debug("Setting up parameters")
    params = {}

    if is_external:
        # External parameters are in the form
        params = {}
        for param in datasource_schema["params"]:
            if param["name"] in request.form:
                params[param["name"]] = request.form[param["name"]]

        logger.info(f"ExternalDataSource params received {params}")

    else:
        for param in datasource_schema["params"]:
            # Save the files, keep track of which parameter they represent
            if param["name"] in request.files:
                params[param["name"]] = tempfile.NamedTemporaryFile()
                request.files[param["name"]].save(params[param["name"]].name)
                params[param["name"]].seek(0)

        logger.info(f"Saved uploaded files {params}")

    logger.debug("Set up parameters")

    try:
        # Create the datasource
        datasource = datasource_cls(
            # Give file paths instead of file-like objects when not external source.
            **(
                {param_name: tempfile.name for param_name, tempfile in params.items()}
                if not is_external
                else params
            )
        )
        transformer = datasource.to_transformer(transformer_cls)
        graph = backend_class(
            metadata=datasource.metadata(), nodes=transformer.run(), consolidate_edges=True
        )
        # Make the graph
        G = graph.graph()

    except Exception as e:
        logger.critical(f"Failure to generate graph {e}")
        import traceback

        logger.debug(f"{traceback.format_exc()}")

        if not is_external:
            # Clean up temporary files
            try:
                for _tempfile in params.values():
                    _tempfile.close()
            except Exception as e:
                logger.critical(f"Failure to clean up temporary files after error {e}")

        response = make_response(jsonify({"message": str(e)}), 500)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    logger.info("Cleaning up tempfiles")

    if not is_external:
        # Clean up temporary files
        for _tempfile in params.values():
            _tempfile.close()

    logger.info("Finished generating graph")

    # Check if we even had a graph.
    # This will be on the G attribute for any class subclassing NetworkX
    if graph.is_empty():
        return make_response(jsonify({"message": f"Graph generation resulted in 0 nodes. "}), 400)

    # If the backend is NetworkX, save the graph.
    # Otherwise, redirect the user to wherever he sent it (if possible)
    if backend_class.__name__ == "NetworkX":

        # Take the SHA256 of the contents of the graph.
        contents_hash = hashlib.sha256(
            json.dumps(graph.to_json(), sort_keys=True).encode("utf-8")
        ).hexdigest()

        # See if we have previously generated this *exact* graph.
        existing = Graph.query.filter_by(meta=graph.metadata, sha256=contents_hash).first()

        if existing:
            logger.info(f"Graph previously generated with id {existing.id}")
            response = jsonify({"id": existing.id, "self": f"/{existing.category}/{existing.id}"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        dest_folder = datasource_cls.category.replace(" ", "_").lower()
        # Set up the storage directory.
        dest_path = f"{Config.get('storage', 'dir')}/{dest_folder}/{contents_hash}.json"
        os.makedirs(f"{Config.get('storage', 'dir')}/{dest_folder}", exist_ok=True)

        db_entry = Graph(
            sha256=contents_hash,
            meta=graph.metadata,
            comment=request.form.get("comment", None),
            category=dest_folder,  # Categories use the lower name!
            file_path=f"{contents_hash}.json",
        )

        db.session.add(db_entry)
        db.session.commit()

        logger.info(f"Added graph to database with id={db_entry.id}")

        json.dump(graph.to_json(), open(dest_path, "w"))

        logger.info(f"Saved graph to {dest_path}")

        response = jsonify({"id": db_entry.id, "self": f"/{dest_folder}/{db_entry.id}"})
    else:
        logger.debug(G)
        response = jsonify({"resp": G})

    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@api.route("/adhoc", methods=["POST"])
def adhoc():
    """Allows for ad-hoc transformation of generic JSON Data based on one of two CIM models:

    1. The Beagle CIM Model (defined in `constants.py`)
    2. The OSSEM Model (defined in https://github.com/Cyb3rWard0g/OSSEM)
    """

    valid_cim_formats = ["beagle"]
    data = request.get_json()
    events = data["data"]
    cim_format = data.get("cim", "beagle")

    if str(cim_format).lower() not in valid_cim_formats:
        response = jsonify({"message": f"cim_format must be in {cim_format}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    if not isinstance(events, list):
        events = [events]

    logger.info(f"Beginning ad-hoc graphing request")

    g = JSONData(events).to_graph(consolidate_edges=True)

    logger.info(f"Completed ad-hoc graphing request")

    return jsonify({"data": NetworkX.graph_to_json(g)})


@api.route("/categories/")
@api.route("/categories")
def get_categories():
    """Returns a list of categories as id, name pairs.

    This list is made up of all categories specified in the category field for each
    datasource.

    >>> {
        "id": "vt_sandbox",
        "name": "VT Sandbox"
    }

    Returns
    -------
    List[dict]
    """
    categories = set([source.category for source in DATASOURCES.values()])

    resp = [{"id": category.replace(" ", "_").lower(), "name": category} for category in categories]

    # Show only the responses we upload
    if request.args.get("uploaded"):
        categories = [value[0] for value in db.session.query(Graph.category).distinct()]
        print(categories)
        resp = list(filter(lambda entry: entry["id"] in categories, resp))

    response = jsonify(resp)

    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@api.route("/categories/<string:category>")
def get_category_items(category: str):
    """Returns the set of items that exist in this category, the path to their JSON files, the comment
    made on them, as well as their metadata.

    >>> {
        comment: str,
        file_path: str,
        id: int,
        metadata: Dict[str, Any]
    }

    Returns 404 if the category is invalid.

    Parameters
    ----------
    category : str
        The category to fetch data for.

    Returns
    -------
    List[dict]
    """

    if category not in set(
        [source.category.replace(" ", "_").lower() for source in DATASOURCES.values()]
    ):
        return make_response(jsonify({"message": "Category not found"}), 404)

    # Return reversed.
    category_data = [graph.to_json() for graph in Graph.query.filter_by(category=category).all()][
        ::-1
    ]

    response = jsonify(category_data)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@api.route("/graph/<int:graph_id>")
def get_graph(graph_id: int):
    """Returns the JSON object for this graph. This is a networkx node_data JSON dump:

    >>> {
        directed: boolean,
        links: [
            {...}
        ],
        multigraph: boolean,
        nodes: [
            {...}
        ]
    }

    Returns 404 if the graph is not found.

    Parameters
    ----------
    graph_id : int
        The graph ID to fetch data for

    Returns
    -------
    Dict
        See https://networkx.github.io/documentation/stable/reference/readwrite/generated/networkx.readwrite.json_graph.node_link_graph.html
    """

    graph_obj = Graph.query.filter_by(id=graph_id).first()

    if not graph_obj:
        return make_response(jsonify({"message": "Graph not found"}), 404)

    dest_path = f"{Config.get('storage', 'dir')}/{graph_obj.category}/{graph_obj.file_path}"

    json_data = json.load(open(dest_path, "r"))

    response = jsonify(json_data)

    response.headers.add("Access-Control-Allow-Origin", "*")

    return response


@api.route("/metadata/<int:graph_id>")
def get_graph_metadata(graph_id: int):
    """Returns the metadata for a single graph. This is automatically generated
    by the datasource classes.

    Parameters
    ----------
    graph_id : int
        Graph ID.

    Returns 404 if the graph ID is not found

    Returns
    -------
    Dict
        A dictionary representing the metadata of the current graph.
    """

    graph_obj = Graph.query.filter_by(id=graph_id).first()

    if not graph_obj:
        return make_response(jsonify({"message": "Graph not found"}), 404)

    response = jsonify(graph_obj.meta)

    response.headers.add("Access-Control-Allow-Origin", "*")

    return response
