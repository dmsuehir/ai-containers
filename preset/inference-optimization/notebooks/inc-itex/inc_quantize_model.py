# Copyright (c) 2024 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: skip-file
import sys

try:
    import neural_compressor as inc

    print("neural_compressor version {}".format(inc.__version__))
except:
    try:
        import lpot as inc

        print("LPOT version {}".format(inc.__version__))
    except:
        import ilit as inc

        print("iLiT version {}".format(inc.__version__))

if inc.__version__ == "1.2":
    print(
        "This script doesn't support LPOT 1.2, please install LPOT 1.1, 1.2.1 or newer"
    )
    sys.exit(1)

import math

import alexnet
import mnist_dataset


def save_int8_frezon_pb(q_model, path):
    from tensorflow.python.platform import gfile

    f = gfile.GFile(path, "wb")
    f.write(q_model.graph_def.SerializeToString())
    print("Save to {}".format(path))


class Dataloader(object):
    def __init__(self, batch_size):
        self.batch_size = batch_size

    def __iter__(self):
        (
            x_train,
            y_train,
            label_train,
            x_test,
            y_test,
            label_test,
        ) = mnist_dataset.read_data()
        batch_nums = math.ceil(len(x_test) / self.batch_size)

        for i in range(batch_nums - 1):
            begin = i * self.batch_size
            end = (i + 1) * self.batch_size
            yield x_test[begin:end], label_test[begin:end]

        begin = (batch_nums - 1) * self.batch_size
        yield x_test[begin:], label_test[begin:]


def auto_tune(input_graph_path, yaml_config, batch_size):
    fp32_graph = alexnet.load_pb(input_graph_path)
    from neural_compressor import experimental

    quan = experimental.Quantization(yaml_config)
    dataloader = Dataloader(batch_size)
    quan.model = fp32_graph
    quan.calib_dataloader = dataloader
    quan.eval_dataloader = dataloader
    quan.eval_func = None
    q_model = quan.fit()
    return q_model


yaml_file = "alexnet.yaml"
batch_size = 200
fp32_frezon_pb_file = "fp32_frezon.pb"
int8_pb_file = "alexnet_int8_model.pb"

q_model = auto_tune(fp32_frezon_pb_file, yaml_file, batch_size)
save_int8_frezon_pb(q_model, int8_pb_file)
