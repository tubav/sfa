###########################################################################
#    Copyright (C) 2011 by root                                      
#    <root@FlabFedora2>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
import sys
from sfa.senslab.OARrestapi import OARapi
from sfa.senslab.LDAPapi import LDAPapi
from sfa.senslab.slabdriver import SlabDriver
from sfa.util.config import Config
from sfa.util.xrn import hrn_to_urn, get_authority
from sfa.util.table import SfaTable
from sfa.trust.hierarchy import Hierarchy

AuthHierarchy = Hierarchy()
table = SfaTable()
if not table.exists():
    table.create()
    
def create_top_level_auth_records(hrn):
    """
    Create top level records (includes root and sub authorities (local/remote)
    """
    print>>sys.stderr, "\r\n =========SenslabImport create_top_level_auth_records\r\n"
    urn = hrn_to_urn(hrn, 'authority')
    # make sure parent exists
    parent_hrn = get_authority(hrn)
    if not parent_hrn:
        parent_hrn = hrn
    if not parent_hrn == hrn:
        create_top_level_auth_records(parent_hrn)
        
    
    # create the authority if it doesnt already exist 
    if not AuthHierarchy.auth_exists(urn):
        AuthHierarchy.create_auth(urn)
    
    # create the db record if it doesnt already exist    
    auth_info = AuthHierarchy.get_auth_info(hrn)
   
    auth_record = table.find({'type': 'authority', 'hrn': hrn})

    if not auth_record:
        auth_record = SfaRecord(hrn=hrn, gid=auth_info.get_gid_object(), type="authority", pointer=-1)
        auth_record['authority'] = get_authority(auth_record['hrn'])
        table.insert(auth_record)
        print>>sys.stderr, "\r\n ========= \t\t SenslabImport NO AUTH RECORD \r\n" ,auth_record['authority']
        
    
def import_node(hrn, node):

    # ASN.1 will have problems with hrn's longer than 64 characters
    if len(hrn) > 64:
        hrn = hrn[:64]

    node_record = table.find({'type': 'node', 'hrn': hrn})
    pkey = Keypair(create=True)
    urn = hrn_to_urn(hrn, 'node')
    node_gid = AuthHierarchy.create_gid(urn, create_uuid(), pkey)
    node_record = SfaRecord(hrn=hrn, gid=node_gid, type="node", pointer=node['node_id'])
    node_record['authority'] = get_authority(node_record['hrn'])
    existing_records = table.find({'hrn': hrn, 'type': 'node', 'pointer': node['node_id']})
    if not existing_records:
        table.insert(node_record)
    else:
        existing_record = existing_records[0]
        node_record['record_id'] = existing_record['record_id']
        table.update(node_record)

# person is already a sfa record 
def import_person(person):       
    existing_records = table.find({'hrn': person['hrn'], 'type': 'user'})
    if not existing_records:
        table.insert(person)
    else:
        existing_record = existing_records[0]
        person['record_id'] = existing_record['record_id']
        table.update(person)      
        
        
        
def delete_record( hrn, type):
    # delete the record
    record_list = table.find({'type': type, 'hrn': hrn})
    for record in record_list:
        table.remove(record)
                
                
def main():

    config = Config()
    if not config.SFA_REGISTRY_ENABLED:
        sys.exit(0)
    root_auth = config.SFA_REGISTRY_ROOT_AUTH
    interface_hrn = config.SFA_INTERFACE_HRN
    print interface_hrn, root_auth
    
     # initialize registry db table
    #table = SfaTable()
    #if not table.exists():
    	#table.create()

    # create root authority 
    create_top_level_auth_records(root_auth)
    
    # create s user record for the slice manager
    #Do we need this?
    #SenslabImporter.create_sm_client_record()
    
    # create interface records 
    #Do we need this?
    #SenslabImporter.logger.info("Import: creating interface records")
    #SenslabImporter.create_interface_records()
     # create dict of all existing sfa records
     
    existing_records = {}
    existing_hrns = []
    key_ids = []
    person_keys = {} 
    results = table.find()
    for result in results:
        existing_records[(result['hrn'], result['type'])] = result
        existing_hrns.append(result['hrn'])   
        
    #Get Senslab nodes 
   
    Driver = SlabDriver(config)
    nodes_dict  = Driver.GetNodes()
    print "\r\n NODES8DICT ",nodes_dict
    
    ldap_person_list = Driver.GetPersons()
    print "\r\n PERSONS_LIST ",ldap_person_list

   
    
    #slices_list = SenslabUsers.GetSlices()
    #print "\r\n SLICES_LIST ",slices_list
    
        # Get all Senslab sites
    #sites_dict  = OARImporter.GetSites()
    #print "\r\n sSITES_DICT" , sites_dict
    
     # start importing 
    #for site in sites_dict:
        #site_hrn = interface_hrn + "." + site['login_base']
        ##sfa_logger().info("Importing site: %s" % site_hrn)
	#print "HRN %s %s site existing in hrn ? %s" %( site['login_base'],site_hrn, site_hrn in existing_hrns)
        ## import if hrn is not in list of existing hrns or if the hrn exists
        ## but its not a site record
        #if site_hrn not in existing_hrns or \
            #(site_hrn, 'authority') not in existing_records:
             #print "SITE HRN UNKNOWN" , site, site_hrn
             #site_hrn = SenslabImporter.import_site(interface_hrn, site)
   
        # import node records
    	#for node_id in site['node_ids']:
		#for[node['node_id'] for node in nodes_dict]:
			#print '\r\n \t **NODE_ID %s node %s '%( node_id, node)		
 			#continue 
    for node in nodes_dict:
        hrn =  hostname_to_hrn(interface_hrn, root_auth, node['hostname'])
        if hrn not in existing_hrns or \
        (hrn, 'node') not in existing_records:
            print "\t\t NODE HRN NOT in existing records!" ,hrn
            import_node(hrn, node)

   # import persons
    for person in ldap_person_list:
        if person['hrn'] not in existing_hrns or \
            (person['hrn'], 'user') not in existing_records :
            import_person( person)	
# import slices
        #for slice_id in site['slice_ids']:
		#print >>sys.stderr, "\r\n\r\n \t ^^^^^^^\\\\\\\\\\\\\\\^^^^^^ slice_id  %s  " %(slice_id)    		
		#for sl in slices_list:
			#if slice_id is sl['slice_id']:
				##hrn = slicename_to_hrn(interface_hrn, sl['name'])
				#hrn = email_to_hrn(site_hrn, sl['name'])
				#print >>sys.stderr, "\r\n\r\n^^^^^^^^^^^^^SLICE ID hrn %s  site_hrn %s" %(hrn,site_hrn)    				
				#if hrn not in existing_hrns or \
				#(hrn, 'slice') not in existing_records:
					#SenslabImporter.import_slice(site_hrn, sl)	

					
    # remove stale records    
    system_records = [interface_hrn, root_auth, interface_hrn + '.slicemanager']
    for (record_hrn, type) in existing_records.keys():
        if record_hrn in system_records:
            continue
        
        record = existing_records[(record_hrn, type)]
        if record['peer_authority']:
            continue					



        found = False
        
        if type == 'authority':    
            #for site in sites_dict:
		#print "\t type : authority : ", site
                #site_hrn = interface_hrn + "." + site['login_base']
                #if site_hrn == record_hrn and site['site_id'] == record['pointer']:
            found = True
            print "\t \t Found :", found
            break
                
        elif type == 'user':
            for person in persons:
                if person['hrn'] == record_hrn:
                    found = True
                break
            
        elif type == 'node':
            login_base = get_leaf(get_authority(record_hrn))
            nodename = Xrn.unescape(get_leaf(record_hrn))
            print "type: node :  nodename %s" %(nodename)
            for node in nodes_dict.values():
                if node['hostname'] == nodename :
                    found = True
                    break 
                    
        else:
            continue 
        
        if not found:
            record_object = existing_records[(record_hrn, type)]
            print "\t\t NOT FOUND ! "
            delete_record(record_hrn, type) 
    
if __name__ == "__main__":
    main()    