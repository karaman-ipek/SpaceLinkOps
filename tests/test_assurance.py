from spacelinkops.assurance import AuditLog


def test_audit_chain_detects_tampering():
    log=AuditLog();log.append("a","SUBMIT","1",timestamp="2026-01-01T00:00:00Z");log.append("b","APPROVE","1",timestamp="2026-01-01T00:00:01Z");assert log.verify();object.__setattr__(log._records[0],"actor","tampered");assert not log.verify()
