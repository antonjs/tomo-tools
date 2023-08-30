#!/bin/bash

EXPERIMENT=$1
SAMPLE=$2

curl https://cryoem-logbook.slac.stanford.edu/lgbk/${EXPERIMENT}/ws/samples \
  -H 'Cookie: webauth_at=YAD6QQO60RPfuo2jrgaauqEnhcLUkHHEkS7wqJvc4SdO2QXX28qM/9iw/WhU78NV39nfuGrYFsL0sWiw6LszmjtpBe7KfrH3sDEmigzgVT6rYEX3; session=.eJyrVnIMCPDxdHYM8fT3iw_y93ENjvfJT3fKz89WsqpWgjL1XVMyS_KLlKyilYwMjAwNDA0NdZ1DDAyUYnXgSnwT8xLTU7Gpqa0FADpwHeU.EuKL9w.wquV9We4wrU_NtqfXamcaVCacAc' | jq '.value' > samples.json

for sample in `find . -lname '*'`; do
	echo $sample
	cat samples.json | jq --arg sample `basename ${sample}` '.[] | select(.name == $sample)' > $sample/sample.json
done
