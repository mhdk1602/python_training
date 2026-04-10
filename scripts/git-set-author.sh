#!/bin/bash

REMOTE_URL=$(git config --get remote.origin.url)

if [[ $REMOTE_URL == *"github.com/mhdk1602"* ]]; then
    git config --local user.name "mhdk1602"
    git config --local user.email "mhdk.dinesh@gmail.com"
elif [[ $REMOTE_URL == *"github.com/Hari-Dinesh_bcgprod"* ]]; then
    git config --local user.name "Hari-Dinesh_bcgprod"
    git config --local user.email "Hari.Dinesh@bcg.com"
fi

