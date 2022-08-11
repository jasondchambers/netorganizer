# test_configure doesn't really make sense here because if we 
# have a test adapter for NetorgConfigurationPort - it leaves 
# nothing to test. We could test the real adapter - NetorgConfigurationJsonFileAdapter
# - But I don't want to over-write an actual config file. 
# Maybe have a test mode - where it uses a different filename?
#  . Needs a rethink.