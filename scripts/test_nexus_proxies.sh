#!/bin/bash
# test_nexus_proxies.sh
# Test that Nexus proxies are working correctly

NEXUS_BASE="https://nexus.yourdomain.com/repository"

declare -A NEXUS_REPOS=(
    ["pypi-proxy"]="simple/"
    ["mongodb-proxy"]="repodata/repomd.xml"
    ["npm-proxy"]="react"
    ["hashicorp-proxy"]="repodata/repomd.xml"
)

echo "Testing Nexus Proxy Access"
echo "==========================="

for repo in "${!NEXUS_REPOS[@]}"; do
    path="${NEXUS_REPOS[$repo]}"
    url="$NEXUS_BASE/$repo/$path"
    
    echo -n "Testing $repo... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [[ "$status" == "200" ]]; then
        echo "✓ OK"
    else
        echo "✗ FAILED (HTTP $status)"
    fi
done
