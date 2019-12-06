from networkx import nx
from .base_query import Query, PropsDict
from .edge import EdgeByProps, EdgeByPropsAncestors, EdgeByPropsDescendants, EdgeByPropsReachable


def make_edge_query(
    edge_type: str, descendants=True, ancestors=False, reachable=False, edge_props: PropsDict = {}
) -> Query:
    if reachable or (descendants and reachable):
        return EdgeByPropsReachable(edge_type=edge_type, edge_props=edge_props)
    elif descendants:
        return EdgeByPropsDescendants(edge_type=edge_type, edge_props=edge_props)
    elif ancestors:
        return EdgeByPropsAncestors(edge_type=edge_type, edge_props=edge_props)
    else:
        return EdgeByProps(edge_type=edge_type, edge_props=edge_props)


class FactoryMixin(object):
    """Mixin to prevent Query Factories from calling execute methods.
    """

    def execute_networkx(self, G: nx.graph):
        raise UserWarning("Query factories cannot be called directly")
