from syrupy.extensions.single_file import SingleFileSnapshotExtension


class WebPImageSnapshotExtension(SingleFileSnapshotExtension):
    _file_extension = "webp"
