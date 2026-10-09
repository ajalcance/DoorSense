"""Focused checks for acquisition boundaries, integrity and archive traversal."""
import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import prepare_runtime as setup


class PreparationTests(unittest.TestCase):
    def setUp(self):
        setup.RUNTIME.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=setup.RUNTIME)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_escape_and_symlink_destination_rejected(self):
        with self.assertRaises(ValueError):
            setup.inside(setup.ROOT.parent / "accidental-write")
        link = self.root / "link"
        link.symlink_to(setup.ROOT.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            setup.inside(link / "accidental-write")

    def test_existing_hash_is_verified_without_network(self):
        path = self.root / "asset"
        path.write_bytes(b"verified")
        expected = hashlib.sha256(b"verified").hexdigest()
        with patch.object(setup, "request", side_effect=AssertionError("network must not run")):
            record = setup.download("https://example.invalid/asset", path, expected, 8)
        self.assertEqual(record["sha256"], expected)

    def test_unverified_existing_asset_rejected(self):
        path = self.root / "asset"
        path.write_bytes(b"existing")
        with self.assertRaises(ValueError):
            setup.download("https://example.invalid/asset", path)

    def test_download_wrong_hash_does_not_promote(self):
        path = self.root / "asset"
        with patch.object(setup, "request", return_value=io.BytesIO(b"tampered")):
            with self.assertRaises(ValueError):
                setup.download("https://example.invalid/asset", path, "0" * 64, 8)
        self.assertFalse(path.exists())

    def test_download_wrong_size_does_not_promote(self):
        path = self.root / "asset"
        with patch.object(setup, "request", return_value=io.BytesIO(b"truncated")):
            with self.assertRaises(ValueError):
                setup.download("https://example.invalid/asset", path, size=100)
        self.assertFalse(path.exists())

    def archive(self, name, link=None):
        archive = self.root / "source.tgz"
        with tarfile.open(archive, "w:gz") as output:
            member = tarfile.TarInfo(name)
            if link:
                member.type = tarfile.SYMTYPE
                member.linkname = link
                output.addfile(member)
            else:
                member.size = 5
                output.addfile(member, io.BytesIO(b"bytes"))
        return archive

    def test_archive_traversal_rejected(self):
        with self.assertRaises(tarfile.FilterError):
            setup.safe_extract(self.archive("../escaped"), self.root / "unpacked")
        self.assertFalse((self.root / "escaped").exists())

    def test_archive_external_symlink_rejected(self):
        with self.assertRaises(tarfile.FilterError):
            setup.safe_extract(self.archive("link", link="/etc"), self.root / "unpacked")

    def test_archive_regular_file_works(self):
        setup.safe_extract(self.archive("lib/asset"), self.root / "unpacked")
        self.assertEqual((self.root / "unpacked/lib/asset").read_bytes(), b"bytes")


if __name__ == "__main__":
    unittest.main()
