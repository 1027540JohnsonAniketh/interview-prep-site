import SwiftUI
import WebKit

struct CompanionWebView: UIViewRepresentable {
    let url: URL
    @Binding var isLoading: Bool
    @Binding var loadError: String?

    func makeCoordinator() -> Coordinator {
        Coordinator(isLoading: $isLoading, loadError: $loadError)
    }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.setURLSchemeHandler(context.coordinator.offlineSchemeHandler, forURLScheme: "app")
        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.navigationDelegate = context.coordinator
        isLoading = true
        loadError = nil
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        context.coordinator.isLoading = $isLoading
        context.coordinator.loadError = $loadError
        guard webView.url != url else {
            return
        }
        isLoading = true
        loadError = nil
        webView.load(URLRequest(url: url))
    }

    final class Coordinator: NSObject, WKNavigationDelegate {
        var isLoading: Binding<Bool>
        var loadError: Binding<String?>
        let offlineSchemeHandler = OfflineBundleSchemeHandler()

        init(isLoading: Binding<Bool>, loadError: Binding<String?>) {
            self.isLoading = isLoading
            self.loadError = loadError
        }

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            isLoading.wrappedValue = true
            loadError.wrappedValue = nil
        }

        func webView(_ webView: WKWebView, didCommit navigation: WKNavigation!) {
            isLoading.wrappedValue = false
            loadError.wrappedValue = nil
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            isLoading.wrappedValue = false
            loadError.wrappedValue = nil
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            isLoading.wrappedValue = false
            loadError.wrappedValue = error.localizedDescription
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            isLoading.wrappedValue = false
            loadError.wrappedValue = error.localizedDescription
        }
    }
}
