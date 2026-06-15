import { useState } from "react";
import { Link } from "wouter";
import { useQuery } from "@tanstack/react-query";
import {
  LayoutDashboard,
  Eye,
  FileText,
  Cpu,
  Zap,
  Activity,
  CheckCircle,
  Server,
  TrendingUp,
  ArrowRight,
  Info,
  Clock,
  Database,
  AlertTriangle,
  CheckCircle2,
  FileSpreadsheet,
  Sparkles
} from "lucide-react";

async function fetchStats() {
  const res = await fetch("/api/stats");
  if (!res.ok) throw new Error("Failed to fetch dashboard stats");
  return res.json();
}

async function fetchRecentInspections() {
  const res = await fetch("/api/history/inspections?limit=5");
  if (!res.ok) throw new Error("Failed to fetch recent inspections");
  return res.json();
}

async function fetchRecentAnalyses() {
  const res = await fetch("/api/history/analyses?limit=5");
  if (!res.ok) throw new Error("Failed to fetch recent analyses");
  return res.json();
}

async function fetchRecentProjects() {
  const res = await fetch("/api/history/projects?limit=5");
  if (!res.ok) throw new Error("Failed to fetch recent projects");
  return res.json();
}

function formatTime(isoString?: string) {
  if (!isoString) return "";
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  } catch (e) {
    return "Recently";
  }
}

export default function DashboardPage() {
  const [activeHistoryTab, setActiveHistoryTab] = useState<"inspections" | "analyses" | "projects">("inspections");

  const { data: stats } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: fetchStats,
    refetchInterval: 3000,
  });

  const { data: inspectionsData } = useQuery({
    queryKey: ["recent-inspections"],
    queryFn: fetchRecentInspections,
    refetchInterval: 10000,
  });

  const { data: analysesData } = useQuery({
    queryKey: ["recent-analyses"],
    queryFn: fetchRecentAnalyses,
    refetchInterval: 10000,
  });

  const { data: projectsData } = useQuery({
    queryKey: ["recent-projects"],
    queryFn: fetchRecentProjects,
    refetchInterval: 10000,
  });
  return (
    <>
      <div className="page-header">
        <div className="page-header-icon" style={{ background: "rgba(59,130,246,0.12)", borderColor: "rgba(59,130,246,0.3)", color: "var(--accent-light)" }}>
          <LayoutDashboard size={18} />
        </div>
        <div className="page-header-text">
          <h1>Project Dashboard</h1>
          <p>Real-time engineering metrics, system diagnostics, and quick design tools</p>
        </div>
      </div>

      <div className="page-body flex flex-col gap-6">
        {/* Welcome Glass Banner */}
        <div 
          className="hero-banner-glass flex flex-col gap-2"
          style={{
            background: "linear-gradient(135deg, rgba(20, 32, 64, 0.4) 0%, rgba(13, 20, 33, 0.9) 100%)",
            border: "1px solid rgba(59, 130, 246, 0.35)",
            padding: "28px",
            boxShadow: "0 10px 40px rgba(59, 130, 246, 0.15), inset 0 1px 1px rgba(255, 255, 255, 0.05)"
          }}
        >
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center" style={{ background: "rgba(139,92,246,0.18)", border: "1px solid rgba(139,92,246,0.4)", color: "var(--accent-light)", padding: "6px", borderRadius: "var(--radius-sm)" }}>
              <Sparkles size={16} />
            </div>
            <h2 style={{ fontSize: "1.25rem", fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
              SpecSense AI Control Center
            </h2>
          </div>
          <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", maxWidth: "800px", lineHeight: 1.6, margin: 0 }}>
            Automate cable specification parsing, inspect structural cable cross-sections with computer vision (YOLOv8), 
            and run intelligent feeder calculations. Access specialized modules via the sidebar or quick actions below.
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="metrics-grid">
          <div 
            className="metric-card metric-card-glow" 
            style={{ 
              background: "linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(13, 20, 33, 0.85) 100%)",
              border: "1px solid rgba(59, 130, 246, 0.25)",
              position: "relative",
              paddingLeft: "24px"
            }}
          >
            <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: "4px", background: "var(--accent)" }} />
            <div className="flex justify-between items-start">
              <div>
                <p className="metric-label" style={{ color: "var(--accent-light)" }}>Vision Inspections</p>
                <p className="metric-value">{stats?.total_inspections ?? 0}</p>
              </div>
              <div style={{ color: "var(--accent-light)", padding: "4px" }}><Eye size={18} /></div>
            </div>
            <p className="metric-sub">Cable images analyzed</p>
          </div>

          <div 
            className="metric-card metric-card-glow" 
            style={{ 
              background: "linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(13, 20, 33, 0.85) 100%)",
              border: "1px solid rgba(139, 92, 246, 0.25)",
              position: "relative",
              paddingLeft: "24px"
            }}
          >
            <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: "4px", background: "var(--accent2)" }} />
            <div className="flex justify-between items-start">
              <div>
                <p className="metric-label" style={{ color: "#a78bfa" }}>Datasheet OCR</p>
                <p className="metric-value">{stats?.total_analyses ?? 0}</p>
              </div>
              <div style={{ color: "var(--accent2)", padding: "4px" }}><FileText size={18} /></div>
            </div>
            <p className="metric-sub">Documents parsed & validated</p>
          </div>

          <div 
            className="metric-card metric-card-glow" 
            style={{ 
              background: "linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(13, 20, 33, 0.85) 100%)",
              border: "1px solid rgba(34, 197, 94, 0.25)",
              position: "relative",
              paddingLeft: "24px"
            }}
          >
            <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: "4px", background: "var(--success)" }} />
            <div className="flex justify-between items-start">
              <div>
                <p className="metric-label" style={{ color: "#4ade80" }}>Feeder Sizing</p>
                <p className="metric-value">{stats?.total_projects ?? 0}</p>
              </div>
              <div style={{ color: "var(--success)", padding: "4px" }}><Cpu size={18} /></div>
            </div>
            <p className="metric-sub">Wiring calculations saved</p>
          </div>

          <div 
            className="metric-card metric-card-glow" 
            style={{ 
              background: "linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(13, 20, 33, 0.85) 100%)",
              border: "1px solid rgba(6, 182, 212, 0.25)",
              position: "relative",
              paddingLeft: "24px"
            }}
          >
            <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: "4px", background: "var(--info)" }} />
            <div className="flex justify-between items-start">
              <div>
                <p className="metric-label" style={{ color: "#22d3ee" }}>DB Connection</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="pulse-glow-dot" />
                  <span className="font-bold text-success text-sm">Online</span>
                </div>
              </div>
              <div style={{ color: "var(--info)", padding: "4px" }}><Database size={18} /></div>
            </div>
            <p className="metric-sub">PostgreSQL system state</p>
          </div>
        </div>

        {/* Available Engineering Modules (Full-width, 3-column Grid) */}
        <div className="flex flex-col gap-4 mt-2">
          <p className="card-title" style={{ margin: 0 }}><Activity size={14} />Available Engineering Modules</p>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
            {[
              {
                title: "OCR Engine",
                desc: "OCR Engine is validation system modules.",
                uptime: "Recent Uptime: 1 hour ago",
                href: "/ocr"
              },
              {
                title: "Vision Module",
                desc: "Transform vision measurements and YOLOv8 validation module.",
                uptime: "Recent Uptime: 1 hour ago",
                href: "/vision"
              },
              {
                title: "Safety Calculator",
                desc: "Safety calculator is representation of wire sizes and overcurrent protections.",
                uptime: "Recent Uptime: 1 hour ago",
                href: "/assistant"
              }
            ].map((m) => (
              <Link key={m.title} href={m.href}>
                <div 
                  className="card" 
                  style={{ 
                    cursor: "pointer", 
                    display: "flex", 
                    flexDirection: "column", 
                    justifyContent: "space-between", 
                    minHeight: "130px", 
                    padding: "20px",
                    transition: "transform var(--transition), border-color var(--transition)"
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = "translateY(-3px)";
                    e.currentTarget.style.borderColor = "var(--border-bright)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "none";
                    e.currentTarget.style.borderColor = "var(--border)";
                  }}
                >
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                      <div className="flex items-center gap-2">
                        <span className="status-dot" style={{ margin: 0, width: "8px", height: "8px" }} />
                        <h3 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>{m.title}</h3>
                      </div>
                      <span className="metric-badge badge-success" style={{ margin: 0, padding: "2px 8px", fontSize: "0.65rem", borderRadius: "4px" }}>ACTIVE</span>
                    </div>
                    <p className="text-xs text-secondary" style={{ lineHeight: 1.5, margin: 0 }}>{m.desc}</p>
                  </div>
                  <p className="text-muted" style={{ fontSize: "0.68rem", margin: "12px 0 0 0" }}>{m.uptime}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Two Columns Section */}
        <div className="result-grid" style={{ gridTemplateColumns: "1.6fr 1.4fr", alignItems: "start", gap: "24px" }}>
          {/* Left: Recent Activity Feed */}
          <div className="card flex flex-col gap-4">
            <div className="flex justify-between items-center">
              <p className="card-title" style={{ margin: 0 }}><Clock size={14} />Recent Activity Log</p>
              <div className="activity-feed-tab">
                <button 
                  className={`activity-feed-tab-btn ${activeHistoryTab === "inspections" ? "active" : ""}`}
                  onClick={() => setActiveHistoryTab("inspections")}
                >
                  <Eye size={12} /> Inspections
                </button>
                <button 
                  className={`activity-feed-tab-btn ${activeHistoryTab === "analyses" ? "active" : ""}`}
                  onClick={() => setActiveHistoryTab("analyses")}
                >
                  <FileSpreadsheet size={12} /> OCR Parser
                </button>
                <button 
                  className={`activity-feed-tab-btn ${activeHistoryTab === "projects" ? "active" : ""}`}
                  onClick={() => setActiveHistoryTab("projects")}
                >
                  <Cpu size={12} /> Projects
                </button>
              </div>
            </div>

            <div className="flex flex-col" style={{ background: "rgba(8,12,20,0.3)", borderRadius: "var(--radius-md)", border: "1px solid var(--border)", overflow: "hidden" }}>
              {activeHistoryTab === "inspections" && (
                <>
                  {!inspectionsData?.results || inspectionsData.results.length === 0 ? (
                    <div className="p-6 text-center text-xs text-muted">No recent inspections found. Run some scans in the Vision module!</div>
                  ) : (
                    inspectionsData.results.slice(0, 5).map((item: any) => (
                      <div key={item.id} className="activity-item">
                        <div className="activity-icon-container" style={{ color: "var(--accent-light)" }}>
                          <Eye size={14} />
                        </div>
                        <div style={{ flex: 1 }}>
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-xs" style={{ color: "var(--text-primary)" }}>{item.filename}</span>
                            <span className="text-muted" style={{ fontSize: "0.7rem", display: "flex", alignItems: "center", gap: "4px" }}><Clock size={10} /> {formatTime(item.created_at)}</span>
                          </div>
                          <div className="flex gap-2 items-center mt-1">
                            <span className={`tag badge-${item.status === "PASS" ? "success" : "danger"}`} style={{ fontSize: "0.65rem", padding: "1px 6px" }}>
                              {item.status}
                            </span>
                            <span className="text-xs text-secondary font-mono">{item.cable_type} ({item.diameter_mm ? `${item.diameter_mm.toFixed(1)}mm` : "N/A"})</span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </>
              )}

              {activeHistoryTab === "analyses" && (
                <>
                  {!analysesData?.results || analysesData.results.length === 0 ? (
                    <div className="p-6 text-center text-xs text-muted">No recent parsed documents found. Run some scans in the OCR module!</div>
                  ) : (
                    analysesData.results.slice(0, 5).map((item: any) => (
                      <div key={item.id} className="activity-item">
                        <div className="activity-icon-container" style={{ color: "var(--accent2)" }}>
                          <FileText size={14} />
                        </div>
                        <div style={{ flex: 1 }}>
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-xs" style={{ color: "var(--text-primary)" }}>{item.filename}</span>
                            <span className="text-muted" style={{ fontSize: "0.7rem", display: "flex", alignItems: "center", gap: "4px" }}><Clock size={10} /> {formatTime(item.created_at)}</span>
                          </div>
                          <div className="flex gap-2 items-center mt-1">
                            <span className="tag badge-accent" style={{ fontSize: "0.65rem", padding: "1px 6px" }}>
                              {item.category || "Document"}
                            </span>
                            <span className="text-xs text-secondary font-mono">
                              Keywords: {item.keywords ? Object.keys(item.keywords).slice(0, 3).join(", ") || "None" : "None"}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </>
              )}

              {activeHistoryTab === "projects" && (
                <>
                  {!projectsData?.results || projectsData.results.length === 0 ? (
                    <div className="p-6 text-center text-xs text-muted">No recent projects found. Calculate some wiring designs in the Technical Assistant!</div>
                  ) : (
                    projectsData.results.slice(0, 5).map((item: any) => (
                      <div key={item.id} className="activity-item">
                        <div className="activity-icon-container" style={{ color: "var(--success)" }}>
                          <Cpu size={14} />
                        </div>
                        <div style={{ flex: 1 }}>
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-xs" style={{ color: "var(--text-primary)" }}>{item.description}</span>
                            <span className="text-muted" style={{ fontSize: "0.7rem", display: "flex", alignItems: "center", gap: "4px" }}><Clock size={10} /> {formatTime(item.created_at)}</span>
                          </div>
                          <div className="flex gap-2 items-center mt-1">
                            <span className="tag badge-success" style={{ fontSize: "0.65rem", padding: "1px 6px" }}>
                              {item.project_type === "feeder" ? "Feeder Sizing" : "Wiring Layout"}
                            </span>
                            <span className="text-xs text-secondary font-mono">
                              {item.recommended_cable ? `Cable: ${item.recommended_cable} mm²` : `Total Load: ${item.total_power_w} W`}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </>
              )}
            </div>
          </div>

          {/* Right: Hardware Status & Tips */}
          <div className="flex flex-col gap-4">
            {/* Hardware / Engine status */}
            <div className="card">
              <p className="card-title" style={{ fontSize: "0.8rem", marginBottom: "12px" }}><Server size={12} />System Environment</p>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted flex items-center gap-1.5">
                    <span className="pulse-glow-dot pulse-blue" /> ML Model Engine:
                  </span>
                  <span className="font-mono text-success font-bold">CUDA (PyTorch 2.5)</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted flex items-center gap-1.5">
                    <span className="pulse-glow-dot pulse-purple" /> OCR Decoder:
                  </span>
                  <span className="font-mono text-accent font-bold">EasyOCR (CPU Enabled)</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted flex items-center gap-1.5">
                    <span className="pulse-glow-dot" /> NLP Parser:
                  </span>
                  <span className="font-mono font-bold">SpaCy Pipelines</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-muted flex items-center gap-1.5">
                    <span className="pulse-glow-dot pulse-warning" /> Web Host:
                  </span>
                  <span className="font-mono font-bold">Uvicorn + FastAPI</span>
                </div>
              </div>
            </div>

            {/* AI Engineering Tips */}
            <div className="alert alert-info flex gap-2" style={{ padding: "12px", border: "1px solid rgba(6,182,212,0.15)" }}>
              <Info size={14} className="text-info" style={{ flexShrink: 0, marginTop: "2px" }} />
              <p style={{ fontSize: "0.75rem", lineHeight: 1.4, margin: 0 }}>
                <strong>Engineering Tip:</strong> Maintain cable voltage drops under 5.0% for distribution networks, and 3.0% for critical branches to avoid efficiency losses.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
