import pytest


@pytest.mark.skip(reason="Not reimplemented yet")
class TestDocViews:
    """pytest-django setting FAIL_INVALID_TEMPLATE_VARS has been set to true. As a result, Django template
    engine will raise an exception on unknown variable"""

    def test_doc_unavailable(self, client):
        response = client.get("/all-rpc/")
        # Forbidden method used -> Django return an HttpNotAllowed
        assert response.status_code == 405

    def test_doc_available(self, client):
        response = client.get("/all-rpc-doc/")
        assert response.status_code == 200
        content = response.rendered_content.replace("\n", "")
        assert "<h3>divide(numerator, denominator, x, y, z, a, b, c)</h3>" in content
        assert "<h6>Parameters:</h6>" in content
        assert "<h6>Return:</h6>" in content
        assert "<em>No documentation available yet</em>" in content
        assert (
            "<li>                            "
            "<strong>numerator</strong>                                                       "
            "     (int or double) -                                                   "
            "     The numerator                        </li>"
        ) in content

    def test_doc_bootstrap4(self, client):
        response = client.get("/all-rpc-doc-bs4/")
        assert response.status_code == 200
        content = response.rendered_content.replace("\n", "")
        assert (
            '        <a data-toggle="collapse" href="#collapse_divide"'
            '           aria-expanded="true" aria-controls="collapse_divide"'
            '           class="text-dark h5 mb-0">'
            "            divide(numerator, denominator, x, y, z, a, b, c)"
            "        </a>"
        ) in content
        assert "<h6>Parameters:</h6>" in content
        assert "<h6>Return:</h6>" in content
        assert "<em>No documentation available yet</em>" in content
        assert (
            "                     <li>"
            "                        <strong>numerator</strong>"
            "                                                    (int or double) -"
            "                                                The numerator"
            "                    </li>"
        ) in content
