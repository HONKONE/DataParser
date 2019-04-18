from BaseStruct import BaseStructParser, FlagErrorException
import struct

LINK_FLAG_ENUM = [
    "HasLinkTargetIDList",
    "HasLinkInfo",
    "HasName",
    "HasRelativePath",
    "HasWorkingDir",
    "HasArguments",
    "HasIconLocation",
    "IsUnicode",
    "ForceNoLinkInfo",
    "HasExpString",
    "RunInSeparateProcess",
    "Unused1",
    "HasDarwinID",
    "RunAsUser",
    "HasExpIcon",
    "NoPidlAlias",
    "Unused2",
    "RunWithShimLayer",
    "ForceNoLinkTrack",
    "EnableTargetMetadata",
    "DisableLinkPathTracking",
    "DisableKnownFolderTracking",
    "DisableKnownFolderAlias",
    "AllowLinkToLink",
    "UnaliasOnSave",
    "PreferEnvironmentPath",
    "KeepLocalIDListForUNCTarget",
]


SHOULD = {
    0x00000001: "SW_SHOWNORMAL",
    0x00000003: "SW_SHOWMAXIMIZED",
    0x00000007: "SW_SHOWMINNOACTIVE",
}

DRIVE_TYPE_ENUM = frozenset({
    0x00000000: "DRIVE_UNKNOWN",
    0x00000001: "DRIVE_NO_ROOT_DIR",
    0x00000002: "DRIVE_REMOVABLE",
    0x00000003: "DRIVE_FIXED",
    0x00000004: "DRIVE_FIXED",
    0x00000005: "DRIVE_FIXED",
    0x00000006: "DRIVE_RAMDISK",
})

NETWORK_PROVIDER_TYPE_ENUM = frozenset({
    0x001A0000: "WNNC_NET_AVID",
    0x001B0000: "WNNC_NET_DOCUSPACE",
    0x001C0000: "WNNC_NET_MANGOSOFT",
    0x001D0000: "WNNC_NET_SERNET",
    0x001E0000: "WNNC_NET_RIVERFRONT1",
    0x001F0000: "WNNC_NET_RIVERFRONT2",
    0x00200000: "WNNC_NET_DECORB",
    0x00210000: "WNNC_NET_PROTSTOR",
    0x00220000: "WNNC_NET_FJ_REDIR",
    0x00230000: "WNNC_NET_DISTINCT",
    0x00240000: "WNNC_NET_TWINS",
    0x00250000: "WNNC_NET_RDR2SAMPLE",
    0x00260000: "WNNC_NET_CSC",
    0x00270000: "WNNC_NET_3IN1",
    0x00290000: "WNNC_NET_EXTENDNET",
    0x002A0000: "WNNC_NET_STAC",
    0x002B0000: "WNNC_NET_FOXBAT",
    0x002C0000: "WNNC_NET_YAHOO",
    0x002D0000: "WNNC_NET_EXIFS",
    0x002E0000: "WNNC_NET_DAV",
    0x002F0000: "WNNC_NET_KNOWARE",
    0x00300000: "WNNC_NET_OBJECT_DIRE",
    0x00310000: "WNNC_NET_MASFAX",
    0x00320000: "WNNC_NET_HOB_NFS",
    0x00330000: "WNNC_NET_SHIVA",
    0x00340000: "WNNC_NET_IBMAL",
    0x00350000: "WNNC_NET_LOCK",
    0x00360000: "WNNC_NET_TERMSRV",
    0x00370000: "WNNC_NET_SRT",
    0x00380000: "WNNC_NET_QUINCY",
    0x00390000: "WNNC_NET_OPENAFS",
    0x003A0000: "WNNC_NET_AVID1",
    0x003B0000: "WNNC_NET_DFS",
    0x003C0000: "WNNC_NET_KWNP",
    0x003D0000: "WNNC_NET_ZENWORKS",
    0x003E0000: "WNNC_NET_DRIVEONWEB",
    0x003F0000: "WNNC_NET_VMWARE",
    0x00400000: "WNNC_NET_RSFX",
    0x00410000: "WNNC_NET_MFILES",
    0x00420000: "WNNC_NET_MS_NFS",
    0x00430000: "WNNC_NET_GOOGLE",
})

class LinkFlagsStruct(BaseStructParser):
    STRUCT = []

    def field_parser(self, stream):
        flag_stream = struct.unpack("<I", stream[self.struct_length: self.struct_length + 4])[0]
        # print bin(flag_stream)
        flag_stream_bin = bin(flag_stream)[2:][::-1]  #LinkFlag https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-shllink/ae350202-3ba9-4790-9e9e-98935f4ee5af
        offset = 0
        for _ in LINK_FLAG_ENUM:
            if offset > len(flag_stream_bin) - 1:
                self.__dict__[_] = 0x0
                self.show_struct_info.append((_, 0))
                continue
            self.__dict__[_] = int(flag_stream_bin[offset])
            self.show_struct_info.append((_, 0))
            offset += 1
        self.struct_length += 4


class StringDataStruct(BaseStructParser):
    STRUCT = [
        ("CountCharacters", 2),
        ("String", u"CountCharacters"),
    ]

    def field_parser(self, stream):
        if type(self.STRUCT[1][1]) == unicode:
            self.String = "".join([self.String[_] for _ in range(0, len(self.String), 2)])

class LinkNameStringStruct(StringDataStruct):
    pass


class LinkRelativePathStringStruct(StringDataStruct):
    pass


class LinkWorkingDirStringStruct(StringDataStruct):
    pass


class LinkArgumentsStringStruct(StringDataStruct):
    pass


class LinkDarwinIDStringStruct(StringDataStruct):
    pass


class LinkExpIconStringStruct(StringDataStruct):
    pass


class EnvironmentVariableDataBlockStruct(BaseStructParser):  #[MS-SHLLINK] 2.5.4 reference by LinkFlagsStruct
    STRUCT = [
        ("BlockSize", 4),
        ("BlockSignature", 4),
        ("TargetAnsi", 260),
        ("TargetUnicode", 520),
    ]

    def check_flag(self):
        if self.BlockSize != 0x00000314:
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "BlockSize must be 0x0314"))
        if self.BlockSignature != 0xA0000001:
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "BlockSignature must be 0xA0000001"))

    def field_parser(self, stream):
        self.TargetAnsi = self.get_str(stream, 8)
        self.TargetUnicode = self.get_str(stream, 260 + 8, unicode)


class DarwinDataBlockStruct(BaseStructParser):
    STRUCT = [
        ("BlockSize", 4),
        ("BlockSignature", 4),
        ("DarwinDataAnsi", 260),
        ("DarwinDataUnicode", 520),
    ]

    def check_flag(self):
        if self.BlockSize != 0x00000314:
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "BlockSize must be 0x0314"))
        if self.BlockSignature != 0xA0000006:
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "BlockSignature must be 0xA0000001"))

    def field_parser(self, stream):
        self.DarwinDataAnsi = self.get_str(stream, 8)
        self.DarwinDataUnicode = self.get_str(stream, 260 + 8, unicode)


class IconEnvironmentDataBlockStruct(EnvironmentVariableDataBlockStruct):
    STRUCT = [
        ("BlockSize", 4),
        ("BlockSignature", 4),
        ("TargetAnsi", 260),
        ("TargetUnicode", 520),
    ]

    def check_flag(self):
        if self.BlockSize != 0x00000314:
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "BlockSize must be 0x0314"))
        if self.BlockSignature != 0xA0000007:
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "BlockSignature must be 0xA0000001"))


class ShimDataBlockStruct(BaseStructParser):
    STRUCT = [
        ("BlockSize", 4),
        ("BlockSignature", 4),
        ("LayerName", 0),
    ]

    def check_flag(self):
        if self.BlockSize <= 0x88:
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "BlockSize must be greater then or equal to 0x88"))
        if self.BlockSignature != 0xA0000008:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSignature must equal to 0xA0000008"))

    def field_parser(self, stream):
        self.LayerName = self.get_str(stream[:self.BlockSize], 8, unicode)
        self.struct_length = self.BlockSize


class TrackerDataBlockStruct(BaseStructParser):
    STRUCT = [
        ("BlockSize", 4),
        ("BlockSignature", 4),
        ("Length", 4),
        ("Version", 4),
        ("MachineID", 16),
        ("Droid", 32),
        ("DroidBirth", 32),
    ]

    def check_flag(self):
        if self.BlockSize != 0x00000060:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSize"))
        if self.BlockSignature != 0xA0000003:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSignature"))
        if self.Length != 0x00000058:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "Length"))
        if self.Version != 0x00000000:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "Version"))


class SerializedPropertyStorageStruct(BaseStructParser):
    STRUCT = [
        ("Storage_Size", 4),
        ("Version", 4),
        ("Format_ID", 16),
        ("Serialized_Property_Value", 0),  #TODO if need parse this struct, it shoud include the struct of  Serialized Property Value
        #TODO but today we don't need parse this property value XD
    ]

    def check_flag(self):
        if self.Version != 0x53505331:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "Version"))

    def field_parser(self, stream):
        if self.Storage_Size == 0x0:
            self.struct_length = 4
        else:
            self.Serialized_Property_Value = stream[24: self.Storage_Size]
            self.struct_length = self.Storage_Size


# [MS-PROPSTORE] https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-propstore/1eb58eb3-e7d8-4a09-ac0e-8bcb14b6fa0e
class PropertyStoreDataBlockStruct(BaseStructParser):
    STRUCT = [
        ("BlockSize", 4),
        ("BlockSignature", 4),
        (SerializedPropertyStorageStruct, 0),
    ]

    def check_flag(self):
        if self.BlockSize != 0x0000000C:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSize"))
        if self.BlockSignature != 0xA0000009:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSignature"))


class SpecialFolderDataBlockStruct(BaseStructParser):
    STRUCT = [
        ("BlockSize", 4),
        ("BlockSignature", 4),
        ("SpecialFolderID", 4),
        ("Offset", 4),
    ]

    def check_flag(self):
        if self.BlockSize != 0x00000010:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSize"))
        if self.BlockSignature != 0xA0000005:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSignature"))


class KnownFolderDataBlockStruct(BaseStructParser): # [MS-LINK] 2.5.6
    STRUCT = [
        ("BlockSize", 4),
        ("BlockSignature", 4),
        ("KnownFolderID", 16),
        ("Offset", 4),
    ]

    def check_flag(self):
        if self.BlockSize != 0x0000001C:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSize"))
        if self.BlockSignature != 0xA000000B:
            raise FlagErrorException(
                "[{0}-{1}]".format(self.__class__.__name__, "BlockSignature"))


class ShellLinkHeaderStruct(BaseStructParser):
    STRUCT = [
        ("HeaderSize", 4),
        ("LinkCLSID", 16),
        (LinkFlagsStruct, 4),
        ("FileAttributes", 4),
        ("CreationTime", 8),
        ("AccessTime", 8),
        ("WriteTime", 8),
        ("FileSize", 4),
        ("IconIndex", 4),
        ("ShowCommand", 4),
        ("HotKey", 2),
        ("Reserved1", 2),
        ("Reserved2", 4),
        ("Reserved3", 4),
    ]

    def check_flag(self):
        if self.LinkCLSID != "0114020000000000c000000000000046":
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "CLSID"))


class IDList(BaseStructParser):
    STRUCT = []
    #ItemID Shell Link (.LNK) Binary File Format 2.2.2

    def get_array(self, stream):
        self.item_list = []
        Id_header = struct.unpack("<H", stream[:2])[0] # if the Id_header is zero, it means the end of ItemID
        while Id_header:
            self.item_list.append(stream[self.struct_length: self.struct_length + Id_header])
            self.struct_length += Id_header
            Id_header = struct.unpack("<H", stream[self.struct_length: self.struct_length + 2])[0]
        self.struct_length += 2 #TerminalID

    def show_struct(self, p=0):
        for _ in self.item_list:
            print "\t"*p, "ItemID Data", _.encode("hex"), "->", str(_)




class LinkTargetIDListStruct(BaseStructParser):
    STRUCT = [
        ("IDListSize", 2),
        ("IDList", [IDList])
    ]


class VolumeIDStruct(BaseStructParser):
    STRUCT = [
        ("VolumeIDSize", 4),
        ("DriveType", 4),
        ("DriveSerialNumber", 4),
        ("VolumeLabelOffset", 4),
        ("VolumeLabelOffsetUnicode", 0),
        ("Data", 0),
    ]

    def field_parser(self, stream):
        if self.VolumeLabelOffset == 0x14:
            self.VolumeLabelOffsetUnicode = struct.unpack("<H", stream[self.Struct_len: self.Struct_len + 4])[0]
            self.struct_length += 4
            self.Data = ""
            for _ in stream[self.VolumeLabelOffsetUnicode:]:
                if ord(_) == 0:
                    break
                else:
                    self.Data += chr(_)
        else:
            self.Data = ""
            for _ in stream[self.VolumeLabelOffset:]:
                if ord(_) == 0:
                    break
                else:
                    self.Data += chr(_)
        self.struct_length = self.VolumeIDSize

    def check_flag(self):
        if self.VolumeIDSize < 0x10: #https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-shllink/b7b3eea7-dbff-4275-bd58-83ba3f12d87a
            raise FlagErrorException("[{0}-{1}]".format(self.__class__.__name__, "VolumeIDSize"))


class CommonNetworkRelativeLinkStruct(BaseStructParser):
    STRUCT = [
        ("CommonNetworkRelativeLinkSize", 4),
        ("CommonNetworkRelativeLinkFlags", 4),
        ("NetNameOffset", 4),
        ("DeviceNameOffset", 4),
        ("NetworkProviderType", 4),
        ("NetNameOffsetUnicode", 0), #OK
        ("DeviceNameOffsetUnicode", 0), #OK
        ("NetName", 0),
        ("DeviceName", 0),
        ("NetNameUnicode", 0), #OK
        ("DeviceNameUnicode", 0), #OK
    ]

    def field_parser(self, stream):
        # self.ValidDevice = (self.CommonNetworkRelativeLinkFlags & 0x1)
        # self.ValidNetType = (self.CommonNetworkRelativeLinkFlags & 0x2) >> 1
        if self.NetNameOffset > 0x14:
            self.NetNameOffsetUnicode = struct.unpack("<I", stream[self.Struct_len:
                                                            self.Struct_len + 4])[0]
            self.struct_length += 4
            self.NetNameUnicode = self.get_str(stream, self.NetNameOffsetUnicode)
            self.DeviceNameOffsetUnicode = struct.unpack("<I", stream[self.Struct_len:
                                                            self.Struct_len + 4])[0]
            self.struct_length += 4
            self.DeviceNameUnicode = self.get_str(stream, self.DeviceNameOffsetUnicode)
        self.NetName = self.get_str(stream, self.NetNameOffset)
        self.DeviceName = self.get_str(stream, self.DeviceNameOffset)
        self.struct_length = self.CommonNetworkRelativeLinkSize



class LinkInfoStruct(BaseStructParser):
    STRUCT = [
        ("LinkInfoSize", 4),
        ("LinkInfoHeaderSize", 4),
        ("LinkInfoFlags", 4),
        ("VolumeIDOffset", 4),
        ("LocalBasePathOffset", 4),
        ("CommonNetworkRelativeLinkOffset", 4),
        ("CommonPathSuffixOffset", 4),
        ("LocalBasePathOffsetUnicode", 0), #option OK
        ("CommonPathSuffixOffsetUnicode ", 0),#option OK
        ("VolumeID", 0),#option OK
        ("LocalBasePath", 0),#option OK
        ("CommonNetworkRelativeLink", 0),#option #OK
        ("CommonPathSuffix", 0),#option OK
        ("LocalBasePathUnicode", 0),#option OK
        ("CommonPathSuffixUnicode", 0),#option OK
    ]

    def field_parser(self, stream):
        self.VolumeIDAndLocalBasePath = (self.LinkInfoFlags & 0x1)
        self.CommonNetworkRelativeLinkAndPathSuffix = (self.LinkInfoFlags & 0x2) >> 1
        self.LocalBasePath = ""
        # self.show_struct()
        if self.LinkInfoHeaderSize >= 0x24:
            self.LocalBasePathOffsetUnicode = struct.unpack("<I", stream[self.Struct_len: self.Struct_len + 4])[0]
            self.struct_length += 4
            self.LocalBasePathUnicode = ""
            for _ in stream[self.LocalBasePathOffsetUnicode:]:
                if ord(_) == 0:
                    break
                else:
                    self.LocalBasePathUnicode += _
            self.CommonPathSuffixOffsetUnicode = struct.unpack("<I", stream[self.Struct_len: self.Struct_len + 4])[0]
            self.CommonPathSuffixUnicode = ""
            for _ in stream[self.CommonPathSuffixOffsetUnicode:]:
                if ord(_) == 0:
                    break
                else:
                    self.CommonPathSuffixUnicode += _
            self.struct_length += 4
        if self.VolumeIDAndLocalBasePath:
            # assert self.VolumeIDOffset == self.Struct_len  #in the normal, the VolumeIDOffset should equal to Struct_len
            self.VolumeID = VolumeIDStruct(stream[self.VolumeIDOffset:])
            for _ in stream[self.LocalBasePathOffset:]:
                if ord(_) == 0:
                    break
                else:
                    self.LocalBasePath += _
        if self.CommonNetworkRelativeLinkAndPathSuffix:
            self.CommonNetworkRelativeLink = CommonNetworkRelativeLinkStruct(stream[self.CommonNetworkRelativeLinkOffset:])
            self.CommonPathSuffix = self.get_str(stream, self.CommonPathSuffixOffset)
        self.struct_length = self.LinkInfoSize


class ParserMain(BaseStructParser):
    STRUCT = []

    def field_parser(self, stream):
        d = stream
        A = ShellLinkHeaderStruct(d)
        self.__dict__[A.__class__.__name__] = A
        self.show_struct_info.append((A, 0))
        d = d[A.Struct_len:]
        if A.LinkFlagsStruct.HasLinkTargetIDList:
            B = LinkTargetIDListStruct(d)
            self.show_struct_info.append((B, 0))
            self.__dict__[B.__class__.__name__] = B
            d = d[B.Struct_len:]
        if A.LinkFlagsStruct.HasLinkInfo and not A.LinkFlagsStruct.ForceNoLinkInfo:
            G = LinkInfoStruct(d)
            self.show_struct_info.append((G, 0))
            self.__dict__[G.__class__.__name__] = G
            d = d[G.Struct_len:]
        if A.LinkFlagsStruct.HasName:
            T = LinkNameStringStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        if A.LinkFlagsStruct.HasRelativePath:
            T = LinkRelativePathStringStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        if A.LinkFlagsStruct.HasWorkingDir:
            T = LinkWorkingDirStringStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        if A.LinkFlagsStruct.HasArguments:
            T = LinkArgumentsStringStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        # if A.LinkFlagsStruct.IsUnicode:
        #     T = StringDataStruct(d)
        #     T.show_struct()
        #     d = d[T.Struct_len:]
        if A.LinkFlagsStruct.HasExpString and A.LinkFlagsStruct.DisableLinkPathTracking:  #TODO: ????
            T = EnvironmentVariableDataBlockStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        if A.LinkFlagsStruct.HasDarwinID:
            T = LinkDarwinIDStringStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        if A.LinkFlagsStruct.HasExpIcon:
            T = LinkExpIconStringStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        if A.LinkFlagsStruct.RunWithShimLayer:
            T = ShimDataBlockStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        if A.LinkFlagsStruct.ForceNoLinkTrack:
            T = TrackerDataBlockStruct(d)
            self.show_struct_info.append((T, 0))
            self.__dict__[T.__class__.__name__] = T
            d = d[T.Struct_len:]
        # if A.LinkFlagsStruct.EnableTargetMetadata: #just a Flag
        #     T = PropertyStoreDataBlockStruct(d)
        #     T.show_struct()
        #     d = d[T.Struct_len:]
        # if not A.LinkFlagsStruct.DisableKnownFolderTracking: ???#TODO if this just a flag???
        #     #INFO: if the DisableKnownFolderTracking is set, it means the struct SpecialFolderDataBlock (section 2.5.9)
        #     # and KnownFolderDataBlock (section 2.5.6) MUST BE IGNORE
        #     T = SpecialFolderDataBlockStruct(d)
        #     T.show_struct()
        #     d = d[T.Struct_len:]
        #     T = KnownFolderDataBlockStruct(d)
        #     T.show_struct()
        #     d = d[T.Struct_len:]


class ShellLinkParserMain:
    def __init__(self, link_parh=None, link_stream=None):
        if link_parh:
            with open(link_parh, 'rb') as fp:
                d = fp.read()
        else:
            d = link_stream
        self.LinkStruct = ParserMain(d)

    def show_full_struct(self):
        self.LinkStruct.show_struct()


import os
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--link_file", type=str, help="the file path of link file which need to parser")
    parser.add_argument("--link_folder", type=str, help="the folder which save link files")
    parser.add_argument("--struct_show", action="store_true", help="show the all fields from the struct")
    parser.add_argument("--extract_command", type=bool, help="show the all fields from the struct", default=True)
    args = parser.parse_args()
    if args.link_file:
        A = ShellLinkParserMain(link_parh=args.link_file)
        if args.extract_command:
            link = ""
            if A.LinkStruct.__dict__.get("LinkRelativePathStringStruct"):
                link += A.LinkStruct.LinkRelativePathStringStruct.String
                link += " "
            if A.LinkStruct.__dict__.get("LinkArgumentsStringStruct"):
                link += A.LinkStruct.LinkArgumentsStringStruct.String
                link += " "
            print "\n" * 4
            print "=========[EMBEDDING-COMMAND]========="
            print link
            print "=========[EMBEDDING-COMMAND]========="
            print "\n" * 4
        if args.struct_show:
            A.show_full_struct()
    else:
        for _ in os.listdir(r"D:\code\New_Hunter\SampleSave"):
            pp = os.path.join(r"D:\code\New_Hunter\SampleSave", _)
            print pp
            A = ShellLinkParserMain(link_parh=pp)
            if args.extract_command:
                link = ""
                if A.LinkStruct.__dict__.get("LinkRelativePathStringStruct"):
                    link += A.LinkStruct.LinkRelativePathStringStruct.String
                    link += " "
                if A.LinkStruct.__dict__.get("LinkArgumentsStringStruct"):
                    link += A.LinkStruct.LinkArgumentsStringStruct.String
                    link += " "
                print "\n" * 4
                print "=========[EMBEDDING-COMMAND]========="
                print link
                print "=========[EMBEDDING-COMMAND]========="
                print "\n" * 4
            if args.struct_show:
                A.show_full_struct()
