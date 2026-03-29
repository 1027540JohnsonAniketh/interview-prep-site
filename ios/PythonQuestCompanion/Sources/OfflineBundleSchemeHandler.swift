import Foundation
import WebKit

final class OfflineBundleSchemeHandler: NSObject, WKURLSchemeHandler {
    private let fileManager = FileManager.default
    private let rootURL: URL?

    override init() {
        self.rootURL = Self.resolveWebRoot()
        super.init()
    }

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let requestURL = urlSchemeTask.request.url else {
            urlSchemeTask.didFailWithError(OfflineBundleError.invalidRequest)
            return
        }

        guard let rootURL else {
            urlSchemeTask.didFailWithError(OfflineBundleError.missingBundleRoot)
            return
        }

        let relativePath = Self.normalizedPath(for: requestURL)
        let candidateURL = rootURL.appendingPathComponent(relativePath)
        let fileURL = resolvedFileURL(from: candidateURL, rootURL: rootURL)

        guard let fileURL else {
            urlSchemeTask.didFailWithError(OfflineBundleError.fileNotFound)
            return
        }

        do {
            let data = try Data(contentsOf: fileURL)
            let response = URLResponse(
                url: requestURL,
                mimeType: Self.mimeType(for: fileURL.pathExtension),
                expectedContentLength: data.count,
                textEncodingName: Self.textEncoding(for: fileURL.pathExtension)
            )
            urlSchemeTask.didReceive(response)
            urlSchemeTask.didReceive(data)
            urlSchemeTask.didFinish()
        } catch {
            urlSchemeTask.didFailWithError(error)
        }
    }

    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}

    private func resolvedFileURL(from candidateURL: URL, rootURL: URL) -> URL? {
        var isDirectory = ObjCBool(false)
        if fileManager.fileExists(atPath: candidateURL.path, isDirectory: &isDirectory) {
            if isDirectory.boolValue {
                let indexURL = candidateURL.appendingPathComponent("index.html")
                return fileManager.fileExists(atPath: indexURL.path) ? indexURL : nil
            }
            return candidateURL
        }

        if candidateURL.pathExtension.isEmpty {
            let indexURL = rootURL.appendingPathComponent("index.html")
            return fileManager.fileExists(atPath: indexURL.path) ? indexURL : nil
        }

        let flattenedURL = rootURL.appendingPathComponent(candidateURL.lastPathComponent)
        if fileManager.fileExists(atPath: flattenedURL.path) {
            return flattenedURL
        }

        return nil
    }

    private static func normalizedPath(for url: URL) -> String {
        let trimmed = url.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        return trimmed.isEmpty ? "index.html" : trimmed
    }

    private static func resolveWebRoot() -> URL? {
        guard let resourceURL = Bundle.main.resourceURL else {
            return nil
        }

        let candidates = [
            resourceURL.appendingPathComponent("frontend", isDirectory: true),
            resourceURL.appendingPathComponent("WebApp", isDirectory: true),
            resourceURL,
        ]

        for candidate in candidates where containsWebApp(at: candidate) {
            return candidate
        }

        let enumerator = FileManager.default.enumerator(
            at: resourceURL,
            includingPropertiesForKeys: nil,
            options: [.skipsHiddenFiles]
        )

        while let nextURL = enumerator?.nextObject() as? URL {
            guard nextURL.lastPathComponent == "index.html" else {
                continue
            }

            let parent = nextURL.deletingLastPathComponent()
            if containsWebApp(at: parent) {
                return parent
            }
        }

        return nil
    }

    private static func containsWebApp(at url: URL) -> Bool {
        let fileManager = FileManager.default
        let requiredFiles = [
            url.appendingPathComponent("index.html").path,
            url.appendingPathComponent("app.js").path,
            url.appendingPathComponent("styles.css").path,
            url.appendingPathComponent("offline-runtime.js").path,
        ]
        return requiredFiles.allSatisfy { fileManager.fileExists(atPath: $0) }
    }

    private static func mimeType(for pathExtension: String) -> String {
        switch pathExtension.lowercased() {
        case "html":
            return "text/html"
        case "css":
            return "text/css"
        case "js", "mjs":
            return "text/javascript"
        case "json", "map":
            return "application/json"
        case "wasm":
            return "application/wasm"
        case "zip":
            return "application/zip"
        case "svg":
            return "image/svg+xml"
        case "png":
            return "image/png"
        case "jpg", "jpeg":
            return "image/jpeg"
        case "webp":
            return "image/webp"
        case "woff2":
            return "font/woff2"
        default:
            return "application/octet-stream"
        }
    }

    private static func textEncoding(for pathExtension: String) -> String? {
        switch pathExtension.lowercased() {
        case "html", "css", "js", "json", "mjs":
            return "utf-8"
        default:
            return nil
        }
    }
}

enum OfflineBundleError: LocalizedError {
    case invalidRequest
    case missingBundleRoot
    case fileNotFound

    var errorDescription: String? {
        switch self {
        case .invalidRequest:
            return "The offline web request was invalid."
        case .missingBundleRoot:
            return "The offline web bundle was not found in the app resources."
        case .fileNotFound:
            return "The requested offline web asset was not found."
        }
    }
}
