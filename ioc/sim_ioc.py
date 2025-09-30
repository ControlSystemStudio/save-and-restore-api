# Import the basic framework components.
from softioc import asyncio_dispatcher, builder, softioc

# Create an asyncio dispatcher, the event loop is now running
dispatcher = asyncio_dispatcher.AsyncioDispatcher()

# Set the record prefix
builder.SetDeviceName("simulated")

# Create records
AA = builder.aOut("A", initial_value=1.0)
BB = builder.aOut("B", initial_value=1.0)
CC = builder.aOut("C", initial_value=1.0)
DD = builder.aOut("D", initial_value=1.0)
EE = builder.aOut("E", initial_value=1.0)
FF = builder.aOut("F", initial_value=1.0)
GG = builder.aOut("G", initial_value=1.0)
HH = builder.aOut("H", initial_value=1.0)
II = builder.aOut("I", initial_value=1.0)
JJ = builder.aOut("J", initial_value=1.0)

# Get the IOC started
builder.LoadDatabase()
softioc.iocInit(dispatcher)

# Finally leave the IOC running with an interactive shell.
# softioc.interactive_ioc(globals())
softioc.non_interactive_ioc()
