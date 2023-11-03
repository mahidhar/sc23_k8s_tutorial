# Scientific Computing with Kubernetes Tutorial

Typical usage workflow\
Hands on session

## Use an existing application container to run jobs



## Simple config files

Let's start with creating a simple test file and import it into a pod.

Create a local file named `hello.txt` with any content you like.

Let's now import this file into a configmap (replace username, as before):
```
kubectl create configmap config1-<username> --from-file=hello.txt
```

Can you see it?
```
kubectl get configmap
```

You can also look at its content with
```
kubectl get configmap -o yaml config1-<username>
```

Import that file into a pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: c1-<username>
spec:
  containers:
  - name: mypod
    image: rockylinux:8
    resources:
      limits:
        memory: 100Mi
        cpu: 100m
      requests:
        memory: 100Mi
        cpu: 100m
    command: ["sh", "-c", "sleep 1000"]
    volumeMounts:
    - name: hello
      mountPath: /tmp/hello.txt
      subPath: hello.txt
  volumes:
  - name: hello
    configMap:
      name: config1-<username>
      items:
      - key: hello.txt
        path: hello.txt
```

Create the pod and once it has started, login using kubectl exec and check if the file is indeed in the /tmp directory.

Inside the pod, try making some changes to 
```
/tmp/hello.txt
```

Cound you open the file for writing?

Once you are done exploring, delete the pod and the configmap:
```
kubectl delete pod c1-<username>
kubectl delete configmap config1-<username> 
```

## Importing a whole directory

Create an additional local file named `world.txt` with any content you like.

Let's now import this file into a configmap (replace username, as before):
```
kubectl create configmap config2-<username> --from-file=hello.txt --from-file=world.txt
```

Check its content, as before.

Let's now import the whole configmap into a pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: c2-<username>
spec:
  containers:
  - name: mypod
    image: rockylinux:8
    resources:
      limits:
        memory: 100Mi
        cpu: 100m
      requests:
        memory: 100Mi
        cpu: 100m
    command: ["sh", "-c", "sleep 1000"]
    volumeMounts:
    - name: cfg
      mountPath: /tmp/myconfig
  volumes:
  - name: cfg
    configMap:
      name: config2-<username>
```

Create the pod and once it has started, login using kubectl exec and check if the file is indeed in the /tmp/myconfig directory.

Once again, try to modify their content.

Log out, and update the content of either hello.txt or world.txt.

Let's now update the configmap:

```
kubectl create configmap config2-<username> --from-file=hello.txt --from-file=world.txt --dry-run=client -o yaml |kubectl replace -f -
```

Log back into the node, and check the content of the files in /tmp/myconfig.

Wait a minute (or so), and check again. The changes should propagate into the running pod. 

Once you are done exploring, delete the pod and the configmap:
```
kubectl delete pod c2-<username>
kubectl delete configmap config2-<username> 
```

## Importing code

Let's now do something (semi) useful. Let's [compute pi](https://www.geeksforgeeks.org/calculate-pi-with-python/).

We'll be using the GitHub repo, since most people prefer using GitHub, but you can use any other git repo for your jobs.

The py calculation code is put to the https://github.com/mahidhar/sc23_k8s_tutorial.

Let's run the compute pi job:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: c3-<username>
spec:
  completions: 1
  ttlSecondsAfterFinished: 1800
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: mypod
        image: cicirello/pyaction:latest
        resources:
          limits:
            memory: 100Mi
            cpu: 1
          requests:
            memory: 100Mi
            cpu: 1
        command: ["sh", "-c", "git clone https://github.com/mahidhar/sc23_k8s_tutorial.git && cd sc23_k8s_tutorial && python3 ./pi.py && echo Done"]
```

Once the pod terminated, check if the result is correct:
```
kubectl logs c3-<usernam>-<hash>
```

You may have noticed that we used the default 1000 steps. Let's get more precision, and use 100000 steps.
Our script can be configured by passing the appropriate environment variable (and no other changes are needed):

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: c3m-<username>
spec:
  completions: 1
  ttlSecondsAfterFinished: 1800
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: mypod
        image: cicirello/pyaction:latest
        env:
        - name: PI_STEPS
          value: "100000"
        resources:
          limits:
            memory: 100Mi
            cpu: 1
          requests:
            memory: 100Mi
            cpu: 1
        command: ["sh", "-c", "git clone https://github.com/PRP-Workshop/PEARC23-code-public.git && cd PEARC23-code-public && python3 ./pi.py && echo Done"]
```

Once the pod terminated, check the result with:
```
kubectl logs c3m-<usernam>-<hash>
```

You should see a result that is slightly different than the before.

You can now delete the jobs:
```
kubectl delete job c3m-<username>
kubectl delete job c3-<username>
```

## Using a secret

What if you don't want to publish the code? In this example we will use the "Fine-grained" personal token just for one repository, but you can use all other secrets the same way (SSH keys, general tokens, etc).

Let's try running the same job, but access the private repo at https://github.com/PRP-Workshop/PEARC23-code-private :

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: c4p-<username>
spec:
  completions: 1
  ttlSecondsAfterFinished: 1800
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: mypod
        image: cicirello/pyaction:latest
        resources:
          limits:
            memory: 100Mi
            cpu: 1
          requests:
            memory: 100Mi
            cpu: 1
        command: ["sh", "-c", "git clone https://github.com/PRP-Workshop/PEARC23-code-private.git && cd PEARC23-code-private && python3 ./pi.py && echo Done"]
```

If you look at the logs (`kubectl logs c4p-<username>-<hash>`), you'll see GitHub complaining about the missing credentials.

Secrets are very similar to configmaps, but provide a little additional protecton for sensitive information.

Let's create the secret with our personal token:

```
kubectl create secret generic github-secret-<username> --from-literal=username=dimm0 --from-literal=token=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
```

**!! Note that we're providing a very limited token for this tutorial. Please don't expose your own private tokens in this public workspace !!**

Let's now use our secret in the job to retrieve the code from our private repo.

Note:
1. remember to replace the username in 3 places
2. if you submit directly from command line using `kubectl create -f - << EOF .... EOF`, you have to escape the `$` character in the command

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: c4pt-<username>
spec:
  completions: 1
  ttlSecondsAfterFinished: 1800
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: mypod
        image: cicirello/pyaction:latest
        env:
        - name: GH_USERNAME
          valueFrom:
            secretKeyRef:
              key: username
              name: github-secret-<username>
        - name: GH_TOKEN
          valueFrom:
            secretKeyRef:
              key: token
              name: github-secret-<username>
        resources:
          limits:
            memory: 100Mi
            cpu: 1
          requests:
            memory: 100Mi
            cpu: 1
        command: ["sh", "-c", "git clone https://$GH_USERNAME:$GH_TOKEN@github.com/PRP-Workshop/PEARC23-code-private.git && cd PEARC23-code-private && python3 ./pi.py && echo Done"]
```

Did the job pull the private code this time?

You can now delete the job. Leave the secret for next tasks.
```
kubectl delete pod c4p-<username>
kubectl delete pod c4pt-<username>
```





