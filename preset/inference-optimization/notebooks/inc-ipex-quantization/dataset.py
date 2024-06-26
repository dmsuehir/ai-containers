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
from typing import List

import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer


class IMDBDataset(Dataset):
    """Dataset with strings to predict pos/neg
    Args:
        text (List[str]): list of strings
        label (List[str]): list of corresponding labels (spam/ham)
        data_size (int): number of data rows to use
    """

    def __init__(
        self,
        text: List[str],
        label: List[str],
        tokenizer: AutoTokenizer,
        max_length: int = 64,
        data_size: int = 1000,
    ):
        if data_size > len(text):
            raise ValueError(f"Maximum rows in dataset {len(text)}")
        self.text = text[:data_size]
        self.label = label
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.text)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.text[idx],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
        )
        item = {key: torch.as_tensor(val) for key, val in encoding.items()}

        return (item, self.label[idx])
