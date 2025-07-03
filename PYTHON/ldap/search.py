import ldap
con = ldap.initialize('ldap://10.14.23.11')

con.simple_bind_s("uid=soumyaranjan.patra,ou=People,dc=xxxxxxxx,dc=com", "sp@xxxxxxxx2020")

ldap_base = "ou=Groups,dc=xxxxxxxx,dc=com"
query = ""
result = con.search_s(ldap_base, ldap.SCOPE_SUBTREE, query)

print(result)