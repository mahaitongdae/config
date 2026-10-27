import AppKit
import Foundation

guard CommandLine.arguments.count == 2 else { exit(2) }
let pb = NSPasteboard.general
var picture: NSImage?
if let images = pb.readObjects(forClasses: [NSImage.self], options: nil) as? [NSImage] {
    picture = images.first
}
if picture == nil, let urls = pb.readObjects(forClasses: [NSURL.self], options: nil) as? [URL], urls.count == 1 {
    picture = NSImage(contentsOf: urls[0])
}
guard let image = picture, let tiff = image.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiff),
      let png = bitmap.representation(using: .png, properties: [:]) else {
    fputs("剪贴板中没有图片。请先截图或复制图片。\n", stderr)
    exit(1)
}
do {
    try png.write(to: URL(fileURLWithPath: CommandLine.arguments[1]), options: .atomic)
} catch {
    fputs("保存剪贴板图片失败：\(error)\n", stderr)
    exit(1)
}
