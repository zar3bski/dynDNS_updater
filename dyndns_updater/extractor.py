class Extractor:
    @classmethod
    def _filter_records(cls, collection, field, expected_value):
        return filter(lambda x: x[field] == expected_value, collection)

    @classmethod
    def extract_first_field_value(cls, collection, filter_field, filter_value, field):
        """get value of the FIRST json record matching FILTER_FIELD in the given COLLECTION"""
        filtered_record = list(cls._filter_records(collection, filter_field, filter_value))
        if len(filtered_record)==1: 
            return filtered_record[0].get(field)
        else: 
            raise ValueError("Multiple records matching FILTER_FIELD")
            