from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from serializers import RegisterExamAttemptSerializer


class ExamRegisterViewSet(viewsets.ViewSet):
    """
    This viewset regiter edx's exam on proctoring service and return generated code
    Required parameters:
    ```
    examCode,
    organization,
    duration,
    reviewedExam,
    reviewerNotes,
    examPassword,
    examSponsor,
    examName,
    ssiProduct,
    orgExtra
    ```

    orgExtra contain json like this:

        {
            "examStartDate": "start_time_str",
            "examEndDate": "end_time_str",
            "noOfStudents": 1,
            "examID": "id"
            "courseID": "course_id",
            "firstName": "first_name",
            "lastName": "last_name",
        }

    """
    serializer_class = RegisterExamAttemptSerializer

    def create(self, request):
        return Response({'status': 'OK'}, status=status.HTTP_201_CREATED)

        # request.data
        # product_resource = ProductResource()
        # result = product_resource.import_data(data, dry_run=True)
        # if result.has_errors():
        #     error_list = {}
        #     for row_number, row in enumerate(result.rows):
        #         if len(row.errors):
        #             error_list[row_number] = []
        #             for error in row.errors:
        #                 error_list[row_number].append(error.error.message)
        #     return Response({"import_errors": error_list},
        #                     status=status.HTTP_400_BAD_REQUEST)
        # result = product_resource.import_data(data, dry_run=False)
        #
        # return Response({'status': 'OK'}, status=status.HTTP_201_CREATED)
