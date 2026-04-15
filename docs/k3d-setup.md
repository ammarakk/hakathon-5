# k3d Setup Guide

## Install k3d (Windows)
Open PowerShell as Admin:
winget install k3d

OR download directly:
https://github.com/k3d-io/k3d/releases
Download: k3d-windows-amd64.exe
Rename to: k3d.exe
Move to: C:\Windows\System32\

## Install k3d (Mac)
brew install k3d

## Install k3d (Linux)
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

## Install kubectl
Windows:
winget install kubectl

Mac:
brew install kubectl

Linux:
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

## Verify Installation
k3d version
kubectl version --client

## Create Cluster
k3d cluster create nur-scents \
  --port "8080:80@loadbalancer" \
  --agents 2

## Verify Cluster
kubectl get nodes
# Should show 3 nodes (1 server + 2 agents)
