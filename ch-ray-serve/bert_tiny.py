from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

semantic_cls = pipeline(Tasks.nli, 'damo/nlp_structbert_nli_chinese-tiny')
semantic_cls(input=('一月份跟二月份肯定有一个月份有.', '肯定有一个月份有'))