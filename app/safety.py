class ExecutionLock:
    """Hard lock for the research build. No order-placement path exists."""
    def __init__(self,cfg):
        self.cfg=cfg
        if cfg.execution_allowed or not cfg.paper_only:
            raise RuntimeError("Execution is disabled in this learning build.")
    def assert_paper_only(self):
        if self.cfg.kill_switch:
            raise RuntimeError("KILL SWITCH ACTIVE")
        if self.cfg.execution_allowed or not self.cfg.paper_only:
            raise RuntimeError("Execution safety check failed.")
        return True
