import { useState } from "react";
import { Link } from "wouter";
import { useQuery, useMutation } from "@tanstack/react-query";
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

async function apiCalculateFeeder(body: object) {
  const res = await fetch("/api/assistant/calculate-feeder", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

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
  const [form, setForm] = useState({
    total_power_w: 12000,
    system_type: "three",
    voltage: 380,
    distance_m: 45,
  });

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

  const mutation = useMutation({ mutationFn: apiCalculateFeeder });
  const res = mutation.data;

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

        {/* Two Columns Section */}
        <div className="result-grid" style={{ gridTemplateColumns: "1.6fr 1.4fr" }}>
          {/* Left: Quick Access Modules & Recent Activity Feed */}
          <div className="flex flex-col gap-6">
            {/* Quick Access Modules */}
            <div className="flex flex-col gap-4">
              <p className="card-title" style={{ margin: 0 }}><Activity size={14} />Available Engineering Modules</p>
              
              <div className="flex flex-col gap-3">
                {[
                  {
                    title: "Vision Inspection",
                    desc: "Analyze cross-section scans of multi-core cable segments to calculate layer dimensions, core diameters, and validate structures against international designs.",
                    icon: Eye,
                    color: "#3b82f6",
                    href: "/vision"
                  },
                  {
                    title: "Datasheet / OCR",
                    desc: "Upload technical cable datasheets in PDF or image format to scan, validate key metrics, log spelling corrections, and auto-generate SEO keywords.",
                    icon: FileText,
                    color: "#8b5cf6",
                    href: "/ocr"
                  },
                  {
                    title: "Technical Assistant",
                    desc: "Size feeder cables according to target capacity/distance or design optimal wiring configurations with full circuit-breaker distributions.",
                    icon: Cpu,
                    color: "#22c55e",
                    href: "/assistant"
                  }
                ].map((m) => {
                  const Icon = m.icon;
                  return (
                    <div key={m.title} className="card flex gap-4 items-start" style={{ transition: "transform 0.2s, border-color 0.2s" }}>
                      <div 
                        style={{ 
                          background: `rgba(${m.color === "#3b82f6" ? "59,130,246" : m.color === "#8b5cf6" ? "139,92,246" : "34,197,150"}, 0.12)`, 
                          border: `1px solid rgba(${m.color === "#3b82f6" ? "59,130,246" : m.color === "#8b5cf6" ? "139,92,246" : "34,197,150"}, 0.3)`, 
                          color: m.color,
                          padding: "10px",
                          borderRadius: "var(--radius-md)"
                        }}
                      >
                        <Icon size={20} />
                      </div>
                      <div style={{ flex: 1 }}>
                        <h3 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>{m.title}</h3>
                        <p className="text-xs text-secondary mt-1" style={{ lineHeight: 1.5 }}>{m.desc}</p>
                        <Link href={m.href}>
                          <a className="text-xs font-bold text-accent flex items-center gap-1 mt-3 hover:underline">
                            Open Module <ArrowRight size={12} />
                          </a>
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Recent Activity Card */}
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
          </div>

          {/* Right: Live Interactive Quick Calculator & Hardware Status */}
          <div className="flex flex-col gap-4">
            <p className="card-title" style={{ margin: 0 }}><Zap size={14} />Interactive Utilities</p>

            {/* Quick Sizer Card */}
            <div className="card">
              <p className="card-title" style={{ fontSize: "0.8rem", marginBottom: "8px" }}><Zap size={12} />Quick Cable Sizer</p>
              <p className="text-xs text-secondary mb-4" style={{ lineHeight: 1.4 }}>
                Compute recommended feeder cable cross-section size and estimate percentage voltage drops.
              </p>
              
              <div className="flex flex-col gap-3">
                <div className="form-group">
                  <label className="form-label" style={{ fontSize: "0.75rem" }}>Total Load (Watts)</label>
                  <input
                    className="form-control"
                    type="number"
                    style={{ padding: "8px 12px" }}
                    value={form.total_power_w}
                    onChange={(e) => setForm(p => ({ ...p, total_power_w: +e.target.value }))}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" style={{ fontSize: "0.75rem" }}>Distance (meters)</label>
                  <input
                    className="form-control"
                    type="number"
                    style={{ padding: "8px 12px" }}
                    value={form.distance_m}
                    onChange={(e) => setForm(p => ({ ...p, distance_m: +e.target.value }))}
                  />
                </div>
                <div className="flex gap-2">
                  <div className="form-group" style={{ flex: 1 }}>
                    <label className="form-label" style={{ fontSize: "0.75rem" }}>Phase</label>
                    <select
                      className="form-control"
                      style={{ padding: "8px 12px" }}
                      value={form.system_type}
                      onChange={(e) => setForm(p => ({
                        ...p,
                        system_type: e.target.value,
                        voltage: e.target.value === "three" ? 380 : 220
                      }))}
                    >
                      <option value="single">Single (220V)</option>
                      <option value="three">Three (380V)</option>
                    </select>
                  </div>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label className="form-label" style={{ fontSize: "0.75rem" }}>Voltage (V)</label>
                    <input
                      className="form-control"
                      type="number"
                      style={{ padding: "8px 12px" }}
                      value={form.voltage}
                      onChange={(e) => setForm(p => ({ ...p, voltage: +e.target.value }))}
                    />
                  </div>
                </div>
                
                <button
                  className="btn btn-primary mt-2"
                  style={{ padding: "10px 14px" }}
                  onClick={() => mutation.mutate(form)}
                  disabled={mutation.isPending}
                >
                  {mutation.isPending ? "Calculating..." : "Calculate Feeder"}
                </button>
              </div>

              {mutation.isError && (
                <div className="alert alert-danger mt-3" style={{ padding: "8px 12px", fontSize: "0.75rem" }}>
                  <span>{(mutation.error as Error).message}</span>
                </div>
              )}

              {res && (
                <div className="mt-4 p-4" style={{ background: "var(--bg-surface)", borderRadius: "var(--radius-md)", border: "1px solid var(--border)" }}>
                  <p className="text-xs font-bold text-accent-light mb-2 flex items-center gap-1">
                    <CheckCircle2 size={12} className="text-success" /> Calculation Result:
                  </p>
                  
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-muted">Recommended Cable:</span>
                      <strong className="font-mono text-success" style={{ fontSize: "0.9rem" }}>{res.recommended_cable_mm2} mm²</strong>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-muted">Calculated Current:</span>
                      <strong className="font-mono">{res.current_a?.toFixed(1)} A</strong>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-muted">Voltage Drop %:</span>
                      <strong className={`font-mono ${res.voltage_drop_status?.includes("WARNING") ? "text-danger" : "text-success"}`}>
                        {res.voltage_drop_pct?.toFixed(1)}%
                      </strong>
                    </div>
                  </div>

                  {/* Cable cross section visualizer schematic */}
                  <div className="cable-cross-section-preview">
                    {(() => {
                      const mm2 = parseFloat(res.recommended_cable_mm2) || 16;
                      // Map mm2 to visual diameter size in pixels (range 25px to 75px)
                      const diameterPx = Math.min(75, Math.max(25, 25 + Math.sqrt(mm2) * 4));
                      return (
                        <div 
                          className="cable-schematic-circle" 
                          style={{ 
                            width: `${diameterPx}px`, 
                            height: `${diameterPx}px`,
                            borderColor: res.voltage_drop_status?.includes("WARNING") ? "var(--warning)" : "var(--success)"
                          }}
                        >
                          <div className="cable-schematic-core" />
                        </div>
                      );
                    })()}
                    <span className="text-muted" style={{ fontSize: "0.6rem", position: "absolute", bottom: "4px", right: "6px" }}>
                      Cross-Section Scale (Dynamic)
                    </span>
                  </div>
                </div>
              )}
            </div>

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
