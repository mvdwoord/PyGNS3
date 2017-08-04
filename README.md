# PyGNS3

is a POC / idea for a python package to interact with [GNS3](http://gns3.com).

It leverages the GNS3 built in API and aims to provide some additional functionality such as custom/bulk interaction with projects and nodes. I have started using GNS3 recently so walking multiple learning curves here. Any ideas / suggestions / constructive criticism is more than welcome.

## GNS3Controller

is the main component interacting with GNS3. It attempts to find a valid gns3_server.conf file to grab IP / port / credentials for the WebAPI. After a succesful connection the controller object holds some basic properties and allow further inspection and interaction with GNS3.

## What is the purpose?

As I am learning and working with GNS3 I'm not sure what exactly this should lead to, but the first thibg that comes to mind is parallel commands towards nodes, or other (bulk) manipulations. Not sure what other scenario's will look like but I guess being able to interact with GNS3 from python could come in handy here or there.

## Example

    import pygns3
    
    controller = pygns3.GNS3Controller()
    print(controller)
    
yields

    GNS3 Controller API endpoint
        Host    127.0.0.1:3080
        Version 2.0.3
        Running 2 Computes
            GNS3 VM
            maartens-MBP.fritz.box
            
    Projects folder /Users/maarten/GNS3/projects
        Basic Cloud Connection
        Basic 4 Routers
    
and    
    
    for compute in controller.computes:
        print("{:30} {}".format(compute['name'], compute['compute_id']))

yields

    GNS3 VM                        11df1f68-23ab-42f5-9a93-af65b7daad2a
    maartens-MBP.fritz.box         local

## Next steps

Implement some sub components and methods on them. Then add some custom functions which operate on multiple nodes or provide command line visualization. Oh and implement telnet interaction of course. Perhaps some configuration diffing or synchronization? who knows.