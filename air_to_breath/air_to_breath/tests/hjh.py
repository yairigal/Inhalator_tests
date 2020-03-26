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
    out = BlockInput()

    def test_method(self):
        print(self.out)
        self.out['a'] += 1



class flow(TestFlow):

    blocks = [
        block,
        block2,
        block2
    ]

