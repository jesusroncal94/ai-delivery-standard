# Authorisation matrix

Guarded file: the human writes or approves every row. Each row has an automated test in CI.

Membership rule: <a user may access a row only if the row's scope key is in the scopes where that user is a member>. The same rule drives database policies, sync scope and file storage.

| Resource | Scope | Actor | Read | Create | Update | Delete | Test |
|---|---|---|---|---|---|---|---|
| <resource> | <scope kind> | owner | | | | | |
| <resource> | <scope kind> | member | | | | | |
| <resource> | <scope kind> | outsider | no | no | no | no | |
| <resource> | <scope kind> | former member | no | no | no | no | |

## Checklist

- [ ] Row-level security (or equivalent) enabled on every exposed table, with checks on both read and write.
- [ ] No view or service path that bypasses the policies; no service key in the client; no authorisation data in user-editable metadata.
- [ ] Revoking membership also stops sync and purges local copies on the next connection.
- [ ] What happens to shared data when a member leaves is decided and written here.
