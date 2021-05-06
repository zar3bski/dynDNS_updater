from itertools import chain


class Extractor:
    @classmethod
    def filter_items(cls, collection, field, expected_value):
        if isinstance(expected_value, (tuple, list)):
            gens = [
                cls.filter_items(collection, field, expected_value[x])
                for x in range(len(expected_value))
            ]
            output = chain()
            for gen in gens:
                output = chain(output, gen)
            return output
        else:
            return filter(lambda x: x[field] == expected_value, collection)

    @classmethod
    def extract_field_value(cls, collection, filter_field, filter_value, field):
        """get value of the FIRST json record matching FILTER_FIELD in the given COLLECTION"""
        filtered_record = list(cls.filter_items(collection, filter_field, filter_value))
        if len(filtered_record) == 1:
            return filtered_record[0].get(field)
        else:
            raise ValueError("Multiple records matching FILTER_FIELD")
