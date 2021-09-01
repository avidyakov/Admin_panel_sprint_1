class Model:
    save: bool = True

    def process_all(self, transfer):
        for raw_field in self._get_raw_fields():
            try:
                getattr(self, f'process_{raw_field}')(transfer)
            except AttributeError:
                continue

    @classmethod
    def _get_raw_fields(cls):
        return [f.name for f in fields(cls) if f.name.startswith('raw_')]

    @classmethod
    def _get_columns(cls):
        return [f.name for f in fields(cls) if not f.name.startswith('raw_') and f != 'save']

    @classmethod
    def export_csv(cls, values):
        file = io.StringIO()
        columns = cls._get_columns()
        writer = csv.DictWriter(file, columns, delimiter=DELIMITER)
        for value in values:
            if value.save:
                filtered_dict = {key: value for key, value in asdict(value).items() if not key.startswith('raw_')}
                writer.writerow(filtered_dict)

        return file, columns

    @classmethod
    def load_data(cls, table_name, rows):
        return (cls(*row) for row in rows)