from syrupy.extensions.single_file import SingleFileSnapshotExtension


class WebPImageSnapshotExtension(SingleFileSnapshotExtension):
    file_extension = "webp"
