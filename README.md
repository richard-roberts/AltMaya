# Toward a decent Maya API

Maya is great but, as almost anyone who uses it comes to realize, also painful to use. One source of significant pain for me is the inconsistent design of `maya.cmds`: I'm forever reading, and then re-reading, the documentation. To avoid dealing with, I'm making a wrapper. My hope is that, as I continue to tweak it, my wrapper provides an clear, concise, and effecient alternative. 

## How do I use it?

Download the source code somewhere that `mayapy` can find, then do `import altmaya`. The source code is relatively minimal for now, so just go look at the modules to see what they can do. 

## Contributing

I haven't settled on a design for the wrappers yet. Feedback, issues, and PRs are most welcome.
