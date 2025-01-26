"""This module will test behavior when library is started"""


# class TestRegistry:
#     """Test internal rpc registry methods"""
#
#     def test_registry_empty_after_reset(self, rpc_registry):
#         # Ensure a normal init registered some rpc methods
#         assert len(rpc_registry.get_all_method_names()) > 0
#         # Reset
#         rpc_registry.reset()
#         # After reset, no mre remote procedure in registry
#         assert len(rpc_registry.get_all_method_names()) == 0
#
#     def test_manual_registration(self, rpc_registry):
#         assert "dummy_remote_procedure_1" not in rpc_registry.get_all_method_names()
#         rpc_registry.register_method(dummy_remote_procedure_1)
#         assert "dummy_remote_procedure_1" in rpc_registry.get_all_method_names()
#
#     def test_double_registration(self, rpc_registry):
#         # Registering twice is not a problem
#         assert "dummy_remote_procedure_1" not in rpc_registry.get_all_method_names()
#         assert rpc_registry.register_method(dummy_remote_procedure_1) == "dummy_remote_procedure_1"
#         assert rpc_registry.register_method(dummy_remote_procedure_1) == "dummy_remote_procedure_1"
#
#     def test_manual_registration_with_different_name(self, rpc_registry):
#         assert "another_name" not in rpc_registry.get_all_method_names()
#         rpc_registry.register_method(dummy_remote_procedure_2)
#         assert "another_name" in rpc_registry.get_all_method_names()
#         assert "dummy_remote_procedure_2" not in rpc_registry.get_all_method_names()
#
#     def test_invalid_custom_name(self, rpc_registry):
#         exc_match = r'method names starting with "rpc." are reserved'
#         with pytest.raises(ImproperlyConfigured, match=exc_match):
#             rpc_registry.register_method(dummy_remote_procedure_3)
#
#         assert "rpc.invalid.name" not in rpc_registry.get_all_method_names()
#         assert "dummy_remote_procedure_3" not in rpc_registry.get_all_method_names()
#
#     def test_duplicated_name(self, rpc_registry):
#         exc_match = r"has already been registered"
#         with pytest.raises(ImproperlyConfigured, match=exc_match):
#             rpc_registry.register_method(dummy_remote_procedure_4)
#
#     def test_duplicated_name_different_entry_points(self, rpc_registry):
#         rpc_registry.register_method(func_v1)
#         rpc_registry.register_method(func_v2)
#
#         v1_wrapper = rpc_registry.get_method("foo", "v1", Protocol.ALL)
#         assert v1_wrapper.function == func_v1
#         assert v1_wrapper.name == "foo"
#         assert v1_wrapper.entry_point == "v1"
#
#         v2_wrapper = rpc_registry.get_method("foo", "v2", Protocol.ALL)
#         assert v2_wrapper.function == func_v2
#         assert v2_wrapper.name == "foo"
#         assert v2_wrapper.entry_point == "v2"
#
#     def test_wrong_manual_registration(self, rpc_registry):
#         # Trying to register a method not decorated now raises an ImproperlyConfigured exception
#         with pytest.raises(ImproperlyConfigured):
#             rpc_registry.register_method(not_decorated_procedure)
#
#     def test_method_names_list(self, rpc_registry):
#         raw_list = rpc_registry.get_all_method_names()
#         sorted_list = rpc_registry.get_all_method_names(sort_methods=True)
#
#         assert len(raw_list) == len(sorted_list)
#         assert raw_list != sorted_list
#
#         for n in raw_list:
#             assert n in sorted_list
#         for n in sorted_list:
#             assert n in raw_list
#
#     def test_methods_list(self, rpc_registry):
#         raw_list = rpc_registry.get_all_methods()
#         sorted_list = rpc_registry.get_all_methods(sort_methods=True)
#
#         assert len(raw_list) == len(sorted_list)
#         assert raw_list != sorted_list
#
#         for m in raw_list:
#             assert m in sorted_list
#
#         for m in sorted_list:
#             assert m in raw_list
#
#     def test_get_methods(self, rpc_registry):
#         methods = rpc_registry.get_all_methods(sort_methods=False)
#         sorted_methods = rpc_registry.get_all_methods(sort_methods=True)
#
#         assert methods != sorted_methods
#         assert len(methods) == len(sorted_methods)
#         # Ensure all methods from on is referenced in other
#         assert all(method in sorted_methods for method in methods)
#         assert all(method in methods for method in sorted_methods)
