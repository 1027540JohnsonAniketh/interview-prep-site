import Foundation
import SwiftUI
import WebKit

struct CompanionWebView: UIViewRepresentable {
    let primaryURL: URL
    let fallbackURL: URL?
    @Binding var isLoading: Bool
    @Binding var loadError: String?
    @Binding var usingFallback: Bool

    func makeCoordinator() -> Coordinator {
        Coordinator(
            isLoading: $isLoading,
            loadError: $loadError,
            usingFallback: $usingFallback
        )
    }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.setURLSchemeHandler(context.coordinator.offlineSchemeHandler, forURLScheme: "app")
        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.navigationDelegate = context.coordinator
        context.coordinator.load(primaryURL: primaryURL, fallbackURL: fallbackURL, in: webView)
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        context.coordinator.isLoading = $isLoading
        context.coordinator.loadError = $loadError
        context.coordinator.usingFallback = $usingFallback
        context.coordinator.load(primaryURL: primaryURL, fallbackURL: fallbackURL, in: webView)
    }

    final class Coordinator: NSObject, WKNavigationDelegate {
        enum LoadTarget {
            case primary
            case fallback
        }

        var isLoading: Binding<Bool>
        var loadError: Binding<String?>
        var usingFallback: Binding<Bool>
        let offlineSchemeHandler = OfflineBundleSchemeHandler()

        private var requestedPrimaryURL: URL?
        private var requestedFallbackURL: URL?
        private var activeTarget: LoadTarget = .primary
        private var attemptedFallback = false

        init(
            isLoading: Binding<Bool>,
            loadError: Binding<String?>,
            usingFallback: Binding<Bool>
        ) {
            self.isLoading = isLoading
            self.loadError = loadError
            self.usingFallback = usingFallback
        }

        func load(primaryURL: URL, fallbackURL: URL?, in webView: WKWebView) {
            if requestedPrimaryURL == primaryURL, requestedFallbackURL == fallbackURL {
                return
            }

            requestedPrimaryURL = primaryURL
            requestedFallbackURL = fallbackURL
            attemptedFallback = false
            activeTarget = .primary
            isLoading.wrappedValue = true
            loadError.wrappedValue = nil
            usingFallback.wrappedValue = false
            webView.load(URLRequest(url: primaryURL))
        }

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            isLoading.wrappedValue = true
            loadError.wrappedValue = nil
        }

        func webView(
            _ webView: WKWebView,
            decidePolicyFor navigationResponse: WKNavigationResponse,
            decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void
        ) {
            guard navigationResponse.isForMainFrame,
                  let response = navigationResponse.response as? HTTPURLResponse,
                  response.statusCode >= 400
            else {
                decisionHandler(.allow)
                return
            }

            if attemptFallback(in: webView) {
                decisionHandler(.cancel)
                return
            }

            decisionHandler(.allow)
        }

        func webView(_ webView: WKWebView, didCommit navigation: WKNavigation!) {
            isLoading.wrappedValue = false
            loadError.wrappedValue = nil
            usingFallback.wrappedValue = activeTarget == .fallback
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            isLoading.wrappedValue = false
            loadError.wrappedValue = nil
            usingFallback.wrappedValue = activeTarget == .fallback
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            handleFailure(error, in: webView)
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            handleFailure(error, in: webView)
        }

        private func handleFailure(_ error: Error, in webView: WKWebView) {
            let nsError = error as NSError
            if nsError.domain == NSURLErrorDomain, nsError.code == NSURLErrorCancelled {
                return
            }

            if attemptFallback(in: webView) {
                return
            }

            isLoading.wrappedValue = false
            loadError.wrappedValue = error.localizedDescription
            usingFallback.wrappedValue = activeTarget == .fallback
        }

        private func attemptFallback(in webView: WKWebView) -> Bool {
            guard activeTarget == .primary,
                  !attemptedFallback,
                  let fallbackURL = requestedFallbackURL
            else {
                return false
            }

            attemptedFallback = true
            activeTarget = .fallback
            isLoading.wrappedValue = true
            loadError.wrappedValue = nil
            usingFallback.wrappedValue = true
            webView.load(URLRequest(url: fallbackURL))
            return true
        }
    }
}
