
def get_network_from_port_context(context):
    network_context_dict = context._network_context
    if network_context_dict is None:
        return None
    return network_context_dict._network
