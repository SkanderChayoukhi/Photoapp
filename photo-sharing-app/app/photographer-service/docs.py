#!/usr/bin/env python3

photographer_metadata = [
    {
        "name": "photographers",
        "description": "Operations on `photographers`",
    },
    {
        "name": "photographer",
        "description": "Operations on `photographer`",
    },
]



create_photographers_doc="""
This operation allows to create a new photographer.
The attributes of the photographer are given in a JSON object passed in the body of the HTTP Request
"""

get_photographers_doc="""
This operation allows to get a list of photographers.
Since a large number of items could be returned by such a call, a pagination system is used. This
is quite common in REST APIs. The `offset` and `limit` are passed as *query* parameters (see example
below) to limit the number of items returned by a single request.

A JSON object is returned in the body of the HTTP response:
* The `items` key is an array of JSON objects with attributes `display_name` and `link` (to the photographer resource).
* The `has_more` key indicates if there are still other items that can be retrieved (by another query).

Moreover, the total count of photographers is returned in the `X-total-count` header of the HTTP response.
"""

head_photographers_doc="""
This operation allows to retrieve the total count of photographers
in the `X-total-count` header of the HTTP response.
"""

put_photographer_doc="""
This operation allows to update a photographer.

In accordance with `PUT` semantics, all attributes of a photographer must be provided.
They will replace the registered attributes.
The `display_name` path param and the `display_name` key of the JSON object representing
the attributes must be identical.
"""

delete_photographer_doc="""
This operation allows to delete a photographer.
"""

get_photographer_doc="""
This operation allows to retrieve the attributes of a photographer.
"""
