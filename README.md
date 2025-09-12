# LLM-Assited Metamorphic Testing

This repository contains a novel approach for generating MRs for MT of embedded graphics libraries using LLMs.
Because directly creating MRs with simple prompts is too complex for the LLM, we employ proven prompting strategies to develop our LLM-assisted MR pipeline.
Strategies include role prompting, least-to-most prompting, zero-shot prompting, constraint-based prompting, and style prompting.
In our experiments, we verify a widely used embedded graphics library. 

## Prerequisites
- Working Python3 environment (including pyelftools, cbor2)
- Transformers package with access to Meta LLAMA 3.1
- [RISC-V GNU Toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain) (multilib recommended)


## Setup Env

1. Clone repository
```
git clone https://github.com/ics-jku/llm-assisted-mt.git
cd llm-assisted-mt
```

2. Install packages and build RISCV-VP++ according to README within riscv-vp-plusplus folder
```
sudo apt install cmake autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo libgoogle-perftools-dev libtool patchutils bc zlib1g-dev libexpat-dev libboost-iostreams-dev libboost-program-options-dev libboost-log-dev qtbase5-dev qt5-qmake libvncserver-dev
cd riscv-vp-plusplus
make -j
cd ..
```
<p color="red">Don't forget to add the RISC-V VP++ bin folder to your $PATH</p>

3. Modify config file
Replace the <ENV_FOLDER> tag with your environment location with the /sut_template/config_template.py file.

## Run Pipeline
Each pipeline step is executed stand alone and the intermediate results are generated into a "results" folder.

```
cd framework
python3 run.py [STEP_NUMBER]
```

Where STEP_NUMBER is numerical from 1-7.

## *LLM-assisted Metamorphic Testing of Embedded Graphics Libraries*

[Christoph Hazott and Daniel Große. LLM-assisted Metamorphic Testing of Embedded Graphics Libraries. Forum on Specification and Design Languages (FDL)](https://ics.jku.at/files/2025FDL_LLMASSISTEDMT.pdf)

```
@inproceedings{HG:2025b,
  title = {{LLM}-assisted Metamorphic Testing of Embedded Graphics Libraries},
  author = {Christoph Hazott and Daniel Gro{\ss}e},
  booktitle = {Forum on Specification and Design Languages (FDL)},
  year = 2025
}
```
