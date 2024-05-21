from rest_framework import serializers

class PandasAI_Excel_Upload_Serializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith(('.xls', '.xlsx')):
            raise serializers.ValidationError('Only .xls and .xlsx files are allowed.')
        valid_mime_types = [
            'application/vnd.ms-excel',  # .xls
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
        ]
        if value.content_type not in valid_mime_types:
            raise serializers.ValidationError('Invalid file type. Only Excel files are allowed.')

        return value

