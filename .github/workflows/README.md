## Want to adapt these workflows to your own project?

- First of all I had to make them run in dockers to get them working on my self-hosted runners.

- They Test by Building the image from the repo, and then running a test on the repos, switching dynamically to what comands are needed to make it work on windows or mac, allowing me to use a mac and windows machine as my two main runners. 
CPU or GPU not needed of course as the script also dynamically choses the right command if running on a machine with GPU or only CPU. 

- ☝️ The reason I made it use docker was to make it very cross compatable in testing, and also becuase of permission errors and such I ran into on both machines. 
Docker became the best solution in this case for me.


For getting your mac used as a runner for these kind of things, I just made my mac launch a docker image that acts as a github runner, 
connected to my macs local docker port.

Example of loop command is seen here
```bash

while true; do
  if [ -S /var/run/docker.sock ]; then
    echo "✅ Docker socket is valid: /var/run/docker.sock"
    docker stop $(docker ps -aq) 2>/dev/null
    docker rm $(docker ps -aq) 2>/dev/null
    docker image prune -f  # This will remove dangling images
    docker run --rm -it \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -e ACCESS_TOKEN="GITHUB_ACCESS_TOKEN" \
      -e REPO_URL="REPO_URL" \
      -e EPHEMERAL="true" \
      -e RUNNER_NAME_PREFIX="Mac-Linux-Ubuntu" \
      myoung34/github-runner
  else
    echo "❌ Docker socket not found or incorrect: /var/run/docker.sock"
    exit 1
  fi
done
```

If your planning on using a ARM archetecture mac as a runer just make sure that docker desktop is set up to use rosetta 2 just in case of potential issues.


## For windows 

- It's pretty simple, Just launch docker and set your windows computer as a workflow normally simple as that. 

Just make sure you run it as a service so it keeps looking for jobs after the first one 








