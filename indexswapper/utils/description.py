from drf_yasg import openapi


API_DESCRIPTIONS = {
    'courseindex_list': '''
        TODO - add docs later :)
    ''',
    'courseindex_retrieve': '''
        TODO - add docs later :)
    ''',
    'courseindex_get_courses': '''
        Get all unique courses code and name (not index!) from all CourseIndex instances.
        All query parameters (pagination / filter / sort) from courseindex_list api are also available here.

        Sample Output:
        ```
        {
            "count": 2,
            "total_pages": 1,
            "results": [
                {
                    "code": "MH1100",
                    "name": "CALCULUS I"
                },
                {
                    "code": "MH1200",
                    "name": "LINEAR ALGEBRA I"
                }
            ]
        }
        ```
    ''',
    'courseindex_get_indexes': '''
        Given a course code (e.g., MH1100), simply return all indexes of that course.
        No pagination / filter / sort feature is implemented here.

        Sample Output:
        ```
        [
            {
                "index": "70181",
                "information": [
                    {
                        "type": "LEC/STUDIO",
                        "group": "LE",
                        "day": "THU",
                        "time": "0930-1020",
                        "venue": "LT27",
                        "remark": ""
                    },
                    ...
                ].
                "pending_count": 1,
            },
            ...
        ]
        ```
    ''',
    'swaprequest_create': '''
        What this endpoint does:
        - Create new SwapRequest instance
        - Email the user for confirmation that SwapRequest instance has been created
        - Perform pairing algorithm for every SwapRequest instance created
        - If any pair is found, email both users that pair has been found

        Expected input data:
        - **contact_info**: _string (max 100 characters)_
            expected contact information preferred by user such as telegram username, phone number, or email
            currently it is free text (no specific format validation)
        - **contact_type**: _string (max 1 character)_
            either 'E' (email) or 'T' (telegram) or 'P' (phone / WhatsApp)
        - **current_index**: _string (max 5 characters)_
            course index that the user currently has and wants to be swapped,
            must be a valid course index (all indexes are unique),
            this user don't have an ongoing SwapRequest with the same index (status S or W)
        - **wanted_indexes**: _list of strings (max 5 characters each, min 1 item in list)_
            list of course indexes that the user wants to swap to,
            each of those index should be valid, should not be the same as current index,
            and should be the same course code as current_index

        Return output:
        - Return 401 if user is not logged in
        - Return 400 bad request if any of the expected input is not present, or
            if it has wrong data type, or if it exceeds max character
        - Return 404 if CourseIndex instance with index 'current_index' does not exist
        - Return 409 if user has an ongoing SwapRequest with the same index (status S or W)
        - Return 400 if any of the index in wanted_indexes is invalid, or if it is the same as current index,
            or if any of the index in wanted_indexes is not the same course code and at least one wanted_index needed,
        - Return 201 with created instance if SwapRequest instance is created successfully
    ''',
    'swaprequest_list': '''
        What this endpoint does:
        - Gets all SwapRequest instances that are created by the user

        Optional query parameters:
        - **status**: _either 'W' or 'S' or 'C'_
            filter SwapRequest instances with this status only
            'W': waiting
            'S': searching
            'C': completed
        
        Return output:
        - Return 401 if user is not logged in
        - Return 400 if query parameter format is invalid
        - Return 200 with list of SwapRequest instances if successful

        Sample output:
        ```
        [
            {
                "id": 1,
                "datetime_added": "2023-07-02 07:29:49",
                "datetime_found": null,
                "wanted_indexes": [
                    "70182",
                    "70183",
                    "70184"
                ],
                "current_index": "70181",
                "contact_info": "@user1zzz",
                "contact_type": "T",
                "status": "W",
                "index_gained": "70184",
                "user": 2,
                "pair": 3
            },
            ...
        ]
        ```
    ''',
    'swaprequest_update': '''
        What this endpoint does:
        - Edit only the `contact_info` and `contact_type` of a SwapRequest instance
        
        It is used in this scenario:
        - User wants to update contact information when SwapRequest status is 'S' (searching) or 'W' (waiting)

        Return output:
        - Return 401 if user is not logged in
        - Return 404 if SwapRequest instance with this id does not exist
        - Return 403 if SwapRequest instance is not created by this user
        - Return 400 if SwapRequest instance status is not 'W' (waiting) or 'S' (searching)
        - Return 200 if successful, along with newly updated data
    ''',
    'swaprequest_search_another': '''
        What this endpoint does:
        - Search another pair (call the swap algorithm again)
        - Send confirmation email

        It is used in this scenario:
        - Current SwapRequest status is 'W' (waiting), means that a pair is found,
        but the pair can't be contacted or has other objection that the swap failed
        - User still wants to search another pair, so this endpoint is called
        - Note that there is a cooldown for 24 hours (adjustable) before you can search another pair again
    
        Return output:
        - Return 401 if user is not logged in
        - Return 404 if SwapRequest instance with this id does not exist
        - Return 403 if SwapRequest instance is not created by this user
        - Return 400 if SwapRequest instance status is not 'W' (waiting),
        or if SwapRequest instance cooldown is not yet expired
        - Return 200 if successful
    ''',
    'swaprequest_mark_complete': '''
        What this endpoint does:
        - Mark current SwapRequest instance as completed
        - Send confirmation email

        It is used in this scenario:
        - Current SwapRequest status is 'W' (waiting), means that a pair is found,
        and the swap has been successfully performed so the user mark it as completed
        *(marking as completed won't affect the status of the pair)
    
        Return output:
        - Return 401 if user is not logged in
        - Return 404 if SwapRequest instance with this id does not exist
        - Return 403 if SwapRequest instance is not created by this user
        - Return 400 if SwapRequest instance status is not 'W' (waiting) or 'S' (searching)
        - Return 200 if successful
    ''',
    'swaprequest_cancel_swap': '''
        What this endpoint does:
        - Cancel a SwapRequest (change the status to 'R' (revoked))
        - If pair is already found, automatically call search algorithm for the pair

        It is used in this scenario:
        - Current SwapRequest status is 'W' (waiting) or 'S' (searching),
        and for some reason the user does not want to swap again

        Return output:
        - Return 401 if user is not logged in
        - Return 404 if SwapRequest instance with this id does not exist
        - Return 403 if SwapRequest instance is not created by this user
        - Return 400 if SwapRequest instance status is not 'W' (waiting) or 'S' (searching)
        - Return 200 if successful
    ''',
}

swaprequest_qp = openapi.Parameter(
    'status', openapi.IN_QUERY,
    description="filter status with 'S'(searching) or 'W'(waiting) or 'C'(completed))",
    type=openapi.TYPE_STRING)

courseindex_search_qp = openapi.Parameter(
    name='search__icontains',
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='Get all CourseIndex with code or name that contains this search string',
    required=False,
)
