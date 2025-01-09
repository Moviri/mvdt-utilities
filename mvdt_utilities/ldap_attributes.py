import win32com.client
from cachetools.func import ttl_cache


class LdapAttributes:
    def __init__(self, ldap_object):
        self.current_time = getattr(ldap_object, "currentTime", None)
        self.subschema_subentry = getattr(ldap_object, "subschemaSubentry", None)
        self.ds_service_name = getattr(ldap_object, "dsServiceName", None)
        self.naming_contexts = getattr(ldap_object, "namingContexts", None)
        self.default_naming_context = getattr(ldap_object, "defaultNamingContext", None)
        self.schema_naming_context = getattr(ldap_object, "schemaNamingContext", None)
        self.configuration_naming_context = getattr(
            ldap_object, "configurationNamingContext", None
        )
        self.root_domain_naming_context = getattr(
            ldap_object, "rootDomainNamingContext", None
        )
        self.supported_control = getattr(ldap_object, "supportedControl", None)
        self.supported_ldap_version = getattr(ldap_object, "supportedLDAPVersion", None)
        self.supported_ldap_policies = getattr(
            ldap_object, "supportedLDAPPolicies", None
        )
        self.highest_committed_usn = getattr(ldap_object, "highestCommittedUSN", None)
        self.supported_sasl_mechanisms = getattr(
            ldap_object, "supportedSASLMechanisms", None
        )
        self.dns_host_name = getattr(ldap_object, "dnsHostName", None)
        self.ldap_service_name = getattr(ldap_object, "ldapServiceName", None)
        self.server_name = getattr(ldap_object, "serverName", None)
        self.supported_capabilities = getattr(
            ldap_object, "supportedCapabilities", None
        )
        self.is_synchronized = getattr(ldap_object, "isSynchronized", None)
        self.is_global_catalog_ready = getattr(
            ldap_object, "isGlobalCatalogReady", None
        )
        self.domain_functionality = getattr(ldap_object, "domainFunctionality", None)
        self.forest_functionality = getattr(ldap_object, "forestFunctionality", None)
        self.domain_controller_functionality = getattr(
            ldap_object, "domainControllerFunctionality", None
        )
        self.name = getattr(ldap_object, "name", None)
        self.parent = getattr(ldap_object, "parent", None)

        # Flexible Single-Master Operation: The distinguished name of the DC where the schema can be modified.
        self.fsmo_owner = getattr(ldap_object, "fSMORoleOwner", None)


# Cache this so that it only runs every 10 minutes
@ttl_cache(maxsize=16, ttl=10 * 60)
def get_ldap_attributes(ldap_path: str) -> LdapAttributes:
    ldap_object = win32com.client.GetObject(ldap_path)
    ldap_object.GetInfo()
    return LdapAttributes(ldap_object)


def get_ldap_attributes_no_cache(ldap_path: str) -> LdapAttributes:
    ldap_object = win32com.client.GetObject(ldap_path)
    ldap_object.GetInfo()
    return LdapAttributes(ldap_object)
