# Scientific Computing with Kubernetes Tutorial

Dealing with data\
Hands on session

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

The py calculation code is put to the https://github.com/PRP-Workshop/PEARC23-code-public

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
        command: ["sh", "-c", "git clone https://github.com/PRP-Workshop/PEARC23-code-public.git && cd PEARC23-code-public && python3 ./pi.py && echo Done"]
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

## Using ephemeral storage

In the past exercizes you have seen that you can write in pretty much any part of the filesystem inside a pod.
But the amount of space you have at your disposal is limited. And if you use a significant portion of it, your pod might be terminated if kubernetes needs to reclaim some node space.

If you need access to a larger (and often faster) local area, you should use the so-called ephemeral storage using emptyDir.

Note that you can request either a disk-based or a memory-based partition. We will do both below.

You can copy-and-paste the lines below, but please do replace “username” with your own id;\
As mentioned before, all the participants in this hands-on session share the same namespace, so you will get name collisions if you don’t.

###### s1.yaml:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: s1-<username>
spec:
  containers:
  - name: mypod
    image: rockylinux:8
    resources:
      limits:
        memory: 8Gi
        cpu: 100m
        ephemeral-storage: 10Gi
      requests:
        memory: 4Gi
        cpu: 100m
        ephemeral-storage: 1Gi
    command: ["sh", "-c", "sleep 1000"]
    volumeMounts:
    - name: scratch1
      mountPath: /mnt/myscratch
    - name: ramdisk1
      mountPath: /mytmp
  volumes:
  - name: scratch1
    emptyDir: {}
  - name: ramdisk1
    emptyDir:
      medium: Memory
```

Create the pod and once it has started, log into it using kubectl exec.

Look at the mounted filesystems:

```
df -H / /mnt/myscratch /tmp /mytmp /dev/shm
```

As you can see, / and /tmp are on the same filesystem, but /mnt/myscratch is a completely different filesystem.

You should also notice that /dev/shm is tiny; the real ramdisk is /mytmp.

*Note:* You can mount the ramdisk as /dev/shm (or /tmp). that way your applications will find it where they expect it to be.

Once you are done exploring, please delete the pod.

## Communicating between containers

Kubernetes allows you to run multiple containers as part of a single pod. Those can share storage volumes and network.
While there are many uses for such a setup, for batch oriented workloads the most useful concept is the initialization pod.

Container images come with a pre-defined setup, and while they may have everything for your main application, 
there may be some tools that are missing for your job initialization. To avoid creating a dedicated image
we can instead use a separate image for the initialization phase, and pass the results using the emphemeral partition.

In previous examples we were using the `cicirello/pyaction` container image, which happened to have the `python` installed together with `git` command. But what if we wanted to use the `tensorflow/tensorflow:2.13.0` image, which doesn't have git installed? We can extent the container image, but also we can use the init container to pull our code.

(replace username in 3 places and escape the dollar sign if you're submitting directly from command line)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: c5-<username>
spec:
  completions: 1
  ttlSecondsAfterFinished: 1800
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: pijob
        image: tensorflow/tensorflow:2.13.0
        resources:
          limits:
            memory: 100Mi
            cpu: 1
          requests:
            memory: 100Mi
            cpu: 1
        command:
        - "python"
        args:
        - "/opt/repo/PEARC23-myrepo/pi.py"
        volumeMounts:
        - name: git-repo
          mountPath: /opt/repo        
      initContainers:
      - name: init-clone-repo
        image: alpine/git
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
        args:
          - clone
          - --single-branch
          - https://$(GH_USERNAME):$(GH_TOKEN)@github.com/PRP-Workshop/PEARC23-code-private.git
          - /opt/repo/PEARC23-myrepo
        volumeMounts:
          - name: git-repo
            mountPath: /opt/repo
      volumes:
      - name: git-repo
        emptyDir: {}
```

We have two containers in this pod, and we can check logs for both. First the clone repo one:

```bash
kubectl logs c5-<username>-<hash> -c init-clone-repo
```

Then the actual job:

```bash
kubectl logs c5-<username>-<hash> -c pijob
```

Once you are done exploring, please delete the job.

## Using persistent storage

Everything we have done so far has been temporary in nature.

The moment you delete the pod, everything that was computed is gone.

Most applications will however need access to long term data for either/both input and output.

In the Kubernetes cluster you are using we have a distributed filesystem, which allows using it for real data persistence.

To get storage, we need to create an object called PersistentVolumeClaim.

By doing that we "Claim" some storage space from a "Persistent Volume".

There will actually be PersistentVolume created, but it's a cluster-wide resource which you can not see.

Create the file (replace username as always):

###### pvc.yaml:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: vol-<username>
spec:
  storageClassName: rook-cephfs
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
```

We're creating a 1GB volume.

Look at it's status with 

```
kubectl get pvc vol-<username>
```
(replace username). 

The `STATUS` field should be equals to `Bound` - this indicates successful allocation.

Note that it may take a few seconds for the system to get there, so be patient.
You can check the progress with

```
kubectl get events --sort-by=.metadata.creationTimestamp --field-selector involvedObject.name=vol-<username>
```

Now we can attach it to our pod. Create one with (replacing `username`):

###### s3.yaml:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: s3-<username>
spec:
  completionMode: Indexed
  completions: 10
  parallelism: 10
  ttlSecondsAfterFinished: 1800
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: mypod
        image: rockylinux:8
        resources:
           limits:
             memory: 100Mi
             cpu: 0.1
           requests:
             memory: 100Mi
             cpu: 0.1
        command: ["sh", "-c", "let s=2*$JOB_COMPLETION_INDEX; d=`date +%s`; date; sleep $s; (echo Job $JOB_COMPLETION_INDEX; ls -l /mnt/mylogs/)  > /mnt/mylogs/log.$d.$JOB_COMPLETION_INDEX; sleep 1000"]
        volumeMounts:
        - name: mydata
          mountPath: /mnt/mylogs
      volumes:
      - name: mydata
        persistentVolumeClaim:
          claimName: vol-<username>
```

Create the job and once any of the pods has started, log into it using kubectl exec.

Check the content of /mnt/mylogs
```
ls -l /mnt/mylogs
```

Try to create a file in there, with any content you like.

Now, delete the job, and create another one (with the same name).

Once one of the new pods start, log into it using kubectl exec.

What do you see in /mnt/mylogs ?

Once you are done exploring, please delete the pod.

If you have time, try to do the same exercise but using emptyDir. And verify that the logs indeed do not get preserved between pod restarts.

## Attaching existing storage

Sometimes you just need to attach to existing storage that is shared between multiple users.

In this cluster we have one CVMFS mountpoint available.

Let's mount it in our pod:

###### s4.yaml:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: s4-<username>
spec:
  containers:
  - name: mypod
    image: rockylinux:8
    resources:
      limits:
        memory: 1Gi
        cpu: 1
      requests:
        memory: 100Mi
        cpu: 100m
    command: ["sleep", "1000"]
    volumeMounts:
    - name: cvmfs
      mountPath: /cvmfs
      readOnly: true
      mountPropagation: HostToContainer
  volumes:
  - name: cvmfs
    persistentVolumeClaim:
      claimName: cvmfs
```


Now let’s start the pod and log into the created pod.

Try to use git:
```
git
```

You will notice it is not present in the image.

So let's use the one on CVMFS, under `osg-software/osg-wn-client`:
```
source /cvmfs/oasis.opensciencegrid.org/osg-software/osg-wn-client/current/el8-x86_64/setup.sh
git
```

Feel free to explore the rest of the mounted filesystem.

When you are done, delete the pod.

## Explicitly moving files in

Most science users have large input data.
If someone has not already pre-loaded them on a PVC, you will have to fetch them yourself.

You can use any tool you are used to, f.e. curl, scp or rclone. You can either pre-load it to a PVC or fetch the data just-in-time, whatever you feel is more appropriate.

We do not have an explicit hands-on tutorial, but feel free to try out your favorite tool using what you have learned so far.

## Handling output data

Unlinke most batch systems, there is no shared filesystem between the submit host (aka your laptop) and the execution nodes.

You are responsible for explicit movement of the output files to a location that is useful for you.

The easiest option is to keep the output files on a persistent PVC and do the follow-up analysis inside the kuberenetes cluster.

But when you want any data to be exported outside of the kubernetes cluster, you will have to do it explicitly.
You can use any (authenticated) file transfer tool from ssh to globus. Just remember to inject the necessary creatials into to pod, ideally using a secret.

For *small files*, you can also use the `kubectl cp` command.
It is similar to `scp`, but routes all traffic through a central kubernetes server, making it very slow.
Good enough for testing and debugging, but not much else. 

Again, we do not have an explict hands-on tutorial, and we discourage the uploading of any sensitive cretentials to this shared kubernetes setup.

## End

**Please make sure you did not leave any running pods. Jobs and associated completed pods are OK.**

