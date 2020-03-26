from rotest.core.block import TestBlock
from rotest.core.flow import TestFlow
from rotest.core.flow_component import BlockInput
from rotest.core.flow_component import BlockOutput


class block(TestBlock):
    out = BlockOutput()

    def test_method(self):
        self.out = {}
        self.out['a'] = 1


class block2(TestBlock):
    out = BlockInput(default=None)

    def test_method(self):
        if self.out is None:
            self.out = {'a': 1}

        print(self.out)
        self.out['a'] += 1


class flow(TestFlow):
    blocks = [
        block,
        block2,
        block2
    ]
