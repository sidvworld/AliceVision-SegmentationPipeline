Welcome to Sid's AliceVision 3D Object Segmentation Pipeline

What does it really do?
AliceVision -> sets up photogrammetry framework/models for 3D scene rescontruction
What my software does -> sets up a 3D object segmentation pipeline, allowing for specific objects from scene reconstructions to be extracted and seperated.

Pretty cool huh!?

Seperate Optimizations:
AliceVision takes advantage of NVIDIA's CUDA Acceleration; however, because my at home PC does not have an NVDIA GPU capable of this, all processes managed out by the sequential command manager for the pipeline is rather streamed to Intels Thread Building Block (TBB) for parallel processing. also pretty cool, a huge headache to figure out!