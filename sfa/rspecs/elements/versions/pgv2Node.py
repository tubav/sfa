
from sfa.util.plxrn import PlXrn
from sfa.util.xrn import Xrn
from sfa.rspecs.elements.element import Element
from sfa.rspecs.elements.node import Node
from sfa.rspecs.elements.sliver import Sliver
from sfa.rspecs.elements.network import Network
from sfa.rspecs.elements.location import Location
from sfa.rspecs.elements.hardware_type import HardwareType
from sfa.rspecs.elements.disk_image import DiskImage
from sfa.rspecs.elements.interface import Interface
from sfa.rspecs.elements.bwlimit import BWlimit
from sfa.rspecs.elements.pltag import PLTag
from sfa.rspecs.elements.versions.pgv2Services import PGv2Services     
from sfa.rspecs.elements.versions.pgv2SliverType import PGv2SliverType     

class PGv2Node:
    @staticmethod
    def add_nodes(xml, nodes):
        node_elems = []
        for node in nodes:
            node_fields = ['component_manager_id', 'component_id', 'client_id', 'sliver_id', 'exclusive']
            elems = Element.add(xml, 'node', node, node_fields)
            node_elem = elems[0]
            node_elems.append(node_elem)
            # set component name
            if node.get('component_id'):
                component_name = Xrn(node['component_id']).get_leaf()
                node_elem.set('component_name', component_name)
            # set hardware types 
            Element.add(node_elem, 'hardware_type', node.get('hardware_types', []), HardwareType.fields.keys()) 
            # set location       
            location_elems = Element.add(node_elem, 'location', node.get('location', []), Location.fields)
            # set interfaces
            interface_elems = Element.add(node_elem, 'interface', node.get('interfaces', []), Interface.fields)
            # set available element
            if node.get('boot_state', '').lower() == 'boot':
                available_elem = node_elem.add_element('available', now='True')
            else:
                available_elem = node_elem.add_element('available', now='False')
            # add services
            PGv2Services.add_services(node_elem, node.get('services', [])) 
            # add slivers
            slivers = node.get('slivers', [])
            if not slivers:
                # we must still advertise the available sliver types
                slivers = Sliver({'type': 'plab-vserver'})
                # we must also advertise the available initscripts
                slivers['tags'] = []
                for initscript in node.get('pl_initscripts', []):
                    slivers['tags'].append({'name': 'initscript', 'value': initscript['name']})
            PGv2SliverType.add_slivers(node_elem, slivers)
        
        return node_elems

    @staticmethod
    def get_nodes(xml, filter={}):
        xpath = '//node%s | //default:node%s' % (XpathFilter.xpath(filter), XpathFilter.xpath(filter))
        node_elems = xml.xpath(xpath)
        return PGv2Node.get_node_objs(node_elems)

    @staticmethod
    def get_nodes_with_sliver(xml):
        xpath = '//node/sliver_type | //default:node/default:sliver_type' 
        node_elems = xml.xpath(xpath)        
        return PGv2Node.get_node_objs(node_elems)

    @staticmethod
    def get_nodes_objs(node_elems):
        nodes = []
        for node_elem in node_elems:
            node = Node(node_elem.attrib, node_elem)
            nodes.append(node) 
            if 'component_id' in node_elem.attrib:
                node['authority_id'] = Xrn(node_elem.attrib['component_id']).get_authority_urn()

            node['hardware_types'] = Element.get(node_elem, './default:hardwate_type | ./hardware_type', HardwareType)
            lolocation_elems = Element.get(node_elem, './default:location | ./location', Location)
            if len(location_elems) > 0:
                node['location'] = location_elems[0]
            node['interfaces'] = Element.get(node_elem, './default:interface | ./interface', Interface)
            node['services'] = PGv2Services.get_services(node_elem)
            node['slivers'] = PGv2SliverType.get_slivers(node_elem)    
            available = Element.get(node_element, './default:available | ./available', fields=['now'])
            if len(available) > 0 and 'name' in available[0].attrib:
                if available[0].attrib.get('now', '').lower() == 'true': 
                    node['boot_state'] = 'boot'
                else: 
                    node['boot_state'] = 'disabled' 
        return nodes


    @staticmethod
    def add_slivers(xml, slivers):
        component_ids = []
        for sliver in slivers:
            filter = {}
            if isinstance(sliver, str):
                filter['component_id'] = '*%s*' % sliver
                sliver = {}
            elif 'component_id' in sliver and sliver['component_id']:
                filter['component_id'] = '*%s*' % sliver['component_id']
            if not filter: 
                continue
            nodes = PGv2Node.get_nodes(xml, filter)
            if not nodes:
                continue
            node = nodes[0]
            PGv2SliverType.add_slivers(node, sliver)

    @staticmethod
    def remove_slivers(xml, hostnames):
        for hostname in hostnames:
            nodes = PGv2Node.get_nodes(xml, {'component_id': '*%s*' % hostname})
            for node in nodes:
                slivers = PGv2SliverType.get_slivers(node.element)
                for sliver in slivers:
                    node.element.remove(sliver.element) 
if __name__ == '__main__':
    from sfa.rspecs.rspec import RSpec
    import pdb
    r = RSpec('/tmp/emulab.rspec')
    r2 = RSpec(version = 'ProtoGENI')
    nodes = PGv2Node.get_nodes(r.xml)
    PGv2Node.add_nodes(r2.xml.root, nodes)
    #pdb.set_trace()
        
                                    