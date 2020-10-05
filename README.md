# OPPORTUNISTIC MEMORY RECLAIM

## Overview

Opportunistic memory reclaim aims to introduce a new interface that allows
user-space to trigger an artificial memory pressure condition and force the
kernel to reclaim memory (dropping page cache pages, swapping out anonymous
memory, etc.).

### Motivation

Reclaiming memory in advance to prepare the system to be more responsive when
needed.

### Use cases

 - Reduce system memory footprint
 - Speed up hibernation time
 - Speed up VM migration time
 - Prioritize responsiveness of foreground applications vs background
   applications
 - Prepare the system to be more responsiveness during large allocation bursts

## Interface

This feature is provided by adding a new file to each memcg:
memory.swap.reclaim.

Writing a number to this file forces a memcg to reclaim memory up to
that number of bytes ("max" means as much memory as possible). Reading
from the this file returns the amount of bytes reclaimed in the last
opportunistic memory reclaim attempt.

Memory reclaim can be interrupted sending a signal to the process that is
writing to memory.swap.reclaim (i.e., to set a timeout for the whole memory
reclaim run).

## Example usage

This feature has been successfully used to improve hibernation time of cloud
computing instances.

Certain cloud providers allow to run "spot instances": low-priority instances
that run when there are spare resources available and can be stopped at any
time to prioritize other more privileged instances [2].

Hibernation can be used to stop these low-priority instances nicely, rather
than losing state when the instance is shut down. Being able to quickly stop
low-priority instances can be critical to provide a better quality of service
in the overall cloud infrastructure [1].

The main bottleneck of hibernation is represented by the I/O generated to write
all the main memory (hibernation image) to a persistent storage.

Opportunistic memory reclaimed can be used to reduce the size of the
hibernation image in advance, for example if the system is idle for a certain
amount of time, so if an hibernation request happens, the kernel has already
saved most of the memory to the swap device (caches have been dropped, etc.)
and hibernation can complete quickly.

## Testing and results

Here is a simple test case to show the effectiveness of this feature.

Environment:
```
   - VM (kvm):
     8GB of RAM
     disk speed: 100 MB/s
     8GB swap file on ext4 (/swapfile)
```

Test case:
```
  - allocate 85% of memory
  - wait for 60s almost in idle
  - hibernate and resume (measuring the time)
```

Result:
  - average of 10 runs tested with `/sys/power/image_size=default` and
    `/sys/power/image_size=0`:
```
                                 5.9-vanilla   5.9-mm_reclaim
                                 -----------   --------------
  [hibernate] image_size=default      49.07s            3.40s
     [resume] image_size=default      18.35s            7.13s

  [hibernate] image_size=0            71.55s            4.72s
     [resume] image_size=0             7.49s            7.41s
```

NOTE #1: in the `5.9-mm_reclaim` case a simple user-space daemon detects when the
system is idle for a certain amount of time and triggers the opportunistic
memory reclaim.

NOTE #2: `/sys/power/image_size=0` can be used with `5.9-vanilla` to speed up
resume time (because it shrinks even more the hibernation image) at the cost of
increasing hibernation time; with `5.9-mm_reclaim` performance are pretty much
the identical in both cases, because the hibernation image is already reduced
to the minimum when the hibernation request happens.

## Conclusion

Being able to trigger memory reclaim from user-space allows to prepare the
system in advance to be more responsive when needed.

This feature has been used with positive test results to speed up hibernation
time of cloud computing instances, but it can also provide benefits to other
use cases, for example:

 - prioritize responsiveness of foreground applications vs background
   applications

 - improve system responsiveness during large allocation bursts (preparing
   system by reclaiming memory in advance, e.g. using some idle cycles)

 - reduce overall system memory footprint (especially in VM / cloud computing
   environments)

## See also

 - [1] https://lwn.net/Articles/821158/
 - [2] https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-interruptions.html
