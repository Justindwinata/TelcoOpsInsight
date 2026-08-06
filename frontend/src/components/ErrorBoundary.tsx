import { Component, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 300 }}>
          <div style={{ textAlign: "center", padding: 32, maxWidth: 500 }}>
            <h2 style={{ fontSize: 18, color: "#1e293b", marginBottom: 8 }}>Something went wrong</h2>
            <p style={{ fontSize: 14, color: "#64748b", marginBottom: 16 }}>
              An unexpected error occurred. Please try again.
            </p>
            <div style={{ fontSize: 12, color: "#dc2626", background: "#fef2f2", padding: 8, borderRadius: 4, marginBottom: 12, textAlign: "left" }}>
              <strong>Error:</strong> {this.state.error?.message || "Unknown error"}
            </div>
            <button onClick={this.handleReset} style={{ padding: "8px 16px", background: "#2563eb", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer" }}>
              Try Again
            </button>
            <button onClick={() => window.location.reload()} style={{ padding: "8px 16px", background: "#64748b", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", marginLeft: 8 }}>
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
