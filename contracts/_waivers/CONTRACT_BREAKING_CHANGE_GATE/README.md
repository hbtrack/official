# CONTRACT_BREAKING_CHANGE_GATE waivers

Waivers para liberar breaking changes **somente** quando:
- o waiver é **machine-readable** e válido;
- o waiver **não está expirado**;
- o `fingerprint.value` corresponde exatamente ao fingerprint publicado no FAIL do gate.

Crie waivers em:

`contracts/_waivers/CONTRACT_BREAKING_CHANGE_GATE/<waiver_name>.json`
