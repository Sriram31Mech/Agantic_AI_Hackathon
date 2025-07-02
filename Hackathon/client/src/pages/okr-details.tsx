import React, { useEffect, useState, useCallback } from "react";
import { useRoute, useLocation } from "wouter";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import FileUploaderTest from '@/components/ui/FileUploaderTest';
import { useToast } from "@/hooks/use-toast";

const API_BASE = "http://localhost:8000/api/get-okr";

const OkrDetails = () => {
  const [match, params] = useRoute("/okr/:id");
  const [, navigate] = useLocation();
  const [okr, setOkr] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openAccordion, setOpenAccordion] = useState<number | null>(null);
  const [evidenceValues, setEvidenceValues] = useState<{ [idx: number]: string | File[] }>({});
  const [selectedFile, setSelectedFile] = useState<File[] | null>(null);
  const { toast } = useToast();

  const generateSubmissionId = (taskId: string) => {
    return `${taskId}-${Date.now()}`;
  };

  const fetchOkrDetails = useCallback(async () => {
    if (!params?.id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/${params.id}`);
      const data = await res.json();
      if (data.result) {
        setOkr(data.result);
      } else {
        setError("OKR not found.");
      }
    } catch (err) {
      setError("Failed to fetch OKR.");
    } finally {
      setLoading(false);
    }
  }, [params?.id]);

  useEffect(() => {
    fetchOkrDetails();
  }, [fetchOkrDetails]);

  const getLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'easy': return '#10B981';
      case 'medium': return '#F59E0B';
      case 'hard': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getLevelBgColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'easy': return 'rgba(16, 185, 129, 0.1)';
      case 'medium': return 'rgba(245, 158, 11, 0.1)';
      case 'hard': return 'rgba(239, 68, 68, 0.1)';
      default: return 'rgba(107, 114, 128, 0.1)';
    }
  };

  const renderEvidenceInput = (hint: string, value: string | File[], setValue: (v: string | File[]) => void) => {
    switch (hint?.toLowerCase()) {
      case 'text':
        return (
          <textarea
            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-purple-400"
            placeholder="Enter your response..."
            value={typeof value === 'string' ? value : ''}
            onChange={e => setValue(e.target.value)}
            rows={4}
          />
        );
      case 'pdf':
      case 'screenshot':
        return <FileUploaderTest onValueChange={setSelectedFile} />;
      case 'linkedin-url':
      case 'git-url':
        return (
          <input
            type="url"
            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-purple-400"
            placeholder={`Paste your ${hint.replace('-url', '').toUpperCase()} URL...`}
            value={typeof value === 'string' ? value : ''}
            onChange={e => setValue(e.target.value)}
          />
        );
      default:
        return (
          <input
            type="text"
            className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-purple-400"
            placeholder="Paste a link or describe your evidence..."
            value={typeof value === 'string' ? value : ''}
            onChange={e => setValue(e.target.value)}
          />
        );
    }
  };

  const handleSubmitEvidence = useCallback(async (taskId: string, okrId: string, evidenceHint: string, submissionContent: string | File[] | null) => {
    let payload: { submission_id: string; okr_id: string; submission_content: string; submission_type: string };

    if (evidenceHint.toLowerCase() === 'pdf' || evidenceHint.toLowerCase() === 'screenshot') {
      if (submissionContent && Array.isArray(submissionContent) && submissionContent.length > 0) {
        const file = submissionContent[0];
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = async () => {
          const base64Content = reader.result as string;
          payload = {
            submission_id: generateSubmissionId(taskId), // Using a unique submission_id
            okr_id: okrId,
            submission_content: base64Content.split(',')[1], // Send only the base64 part
            submission_type: evidenceHint.toLowerCase(),
          };
          await sendValidationRequest(payload);
        };
        reader.onerror = (error) => {
          console.error("Error reading file:", error);
          setError("Failed to read file.");
        };
      } else {
        setError("No file selected for submission.");
        return;
      }
    } else {
      payload = {
        submission_id: generateSubmissionId(taskId), // Using a unique submission_id
        okr_id: okrId,
        submission_content: typeof submissionContent === 'string' ? submissionContent : '',
        submission_type: evidenceHint.toLowerCase(),
      };
      await sendValidationRequest(payload);
    }
  }, []);

  const sendValidationRequest = async (payload: any) => {
    try {
      const response = await fetch("http://localhost:8000/api/okr/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      console.log("Validation response:", data);

      if (response.ok && data.success) {
        toast({
          title: "Validation Successful!",
          description: data.message || "Your evidence has been successfully validated.",
        });
        fetchOkrDetails(); // Refresh OKR details to update task status
      } else {
        toast({
          title: "Validation Failed!",
          description: data.message || "There was an error validating your evidence.",
          variant: "destructive",
        });
      }
    } catch (err) {
      console.error("Error validating OKR:", err);
      toast({
        title: "Request Error",
        description: "Failed to send validation request.",
        variant: "destructive",
      });
      setError("Failed to send validation request.");
    }
  };

  if (loading) return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 flex items-center justify-center">
      <div className="text-white text-center text-2xl font-light">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white mx-auto mb-4"></div>
        Loading...
      </div>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 flex items-center justify-center">
      <div className="text-white text-center text-xl font-light">{error}</div>
    </div>
  );

  if (!okr) return null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
      </div>

      <div className="relative z-10 p-6 md:p-8 lg:p-12">
        <div className="max-w-5xl mx-auto">
          
          {/* Back Button */}
          <div className="mb-8">
            <button
              onClick={() => navigate("/")}
              className="group flex items-center space-x-2 text-white/80 hover:text-white transition-all duration-300 font-medium backdrop-blur-sm bg-white/10 px-4 py-2 rounded-full border border-white/20 hover:border-white/40 hover:bg-white/20"
            >
              <svg className="w-4 h-4 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span>Back to OKRs</span>
            </button>
          </div>

          {/* Header */}
          <div className="mb-12 text-center">
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-8 md:p-12 border border-white/20 shadow-2xl">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent leading-tight">
                {okr.title}
              </h1>

              <p className="text-xl md:text-2xl mb-8 text-white/90 leading-relaxed max-w-4xl mx-auto font-light">
                {okr.description}
              </p>

              <div className="flex flex-col md:flex-row justify-center items-center gap-6 text-white/80">
                <div className="flex items-center space-x-3 backdrop-blur-sm bg-white/10 px-6 py-3 rounded-full border border-white/20">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="font-medium">
                    {okr.targetDate || okr.parsed?.deadline}
                  </span>
                </div>
                <div className="flex items-center space-x-3 backdrop-blur-sm bg-white/10 px-6 py-3 rounded-full border border-white/20">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="font-medium">
                    {okr.status || "N/A"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Micro Tasks */}
          <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-8 md:p-12 border border-white/20 shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-8 text-white text-center">
              Micro Tasks
            </h2>

            {(okr.micro_tasks && okr.micro_tasks.length > 0) ? (
              <div className="grid gap-6 md:gap-8">
                {okr.micro_tasks.map((task: any, idx: number) => (
                  <div
                    key={idx}
                    className="group backdrop-blur-xl bg-white/10 rounded-2xl p-6 md:p-8 border border-white/20 hover:border-white/40 transition-all duration-500 hover:bg-white/15 hover:shadow-2xl hover:scale-[1.02] cursor-pointer"
                  >
                    <div className="flex flex-col md:flex-row md:justify-between md:items-start mb-6 gap-4">
                      <h3 className="text-xl md:text-2xl font-semibold text-white leading-relaxed flex-1">
                        {task.task}
                      </h3>

                      <span
                        className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wider border-2 backdrop-blur-sm transition-all duration-300 group-hover:scale-105"
                        style={{
                          backgroundColor: getLevelBgColor(task.level),
                          color: getLevelColor(task.level),
                          borderColor: getLevelColor(task.level),
                        }}
                      >
                        {task.level || "N/A"}
                      </span>

                      {/* Task Status Display */}
                      <span
                        className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wider border-2 backdrop-blur-sm ${task.status === 'completed' ? 'bg-green-500/20 text-green-200 border-green-400/30' : 'bg-yellow-500/20 text-yellow-200 border-yellow-400/30'}`}
                      >
                        {task.status || "PENDING"}
                        {task.status === 'completed' && (
                          <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </span>

                    </div>

                    <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
                      <div className="flex items-center space-x-3 text-white/80">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-medium">Due:</span>
                        <span className="backdrop-blur-sm bg-indigo-500/20 text-indigo-200 px-3 py-1 rounded-full text-sm font-medium border border-indigo-400/30">
                          {task.due || "No date"}
                        </span>
                      </div>

                      <button
                        className="group/btn backdrop-blur-sm bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300 border border-white/20 hover:border-white/40 hover:shadow-lg hover:scale-105 flex items-center space-x-2"
                        onClick={() => setOpenAccordion(openAccordion === idx ? null : idx)}
                      >
                        <span>Submit Evidence</span>
                        <svg className="w-4 h-4 transition-transform group-hover/btn:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4l8 8-8 8M6 12h14" />
                        </svg>
                      </button>
                    </div>

                    <Accordion type="single" collapsible value={openAccordion === idx ? String(idx) : undefined} onValueChange={() => setOpenAccordion(openAccordion === idx ? null : idx)}>
                      <AccordionItem value={String(idx)}>
                        <h3 className="text-xl font-semibold text-gray-800 mb-4"> Submit Evidence for this Task </h3>
                        <AccordionContent>
                          <form className="space-y-4">
                            <div>
                              <label className="block text-white/80 mb-2">Evidence</label>
                              {renderEvidenceInput(task.evidence_hint, evidenceValues[idx] || (task.evidence_hint.toLowerCase() === 'pdf' || task.evidence_hint.toLowerCase() === 'screenshot' ? [] : ''), v => setEvidenceValues(ev => ({ ...ev, [idx]: v })))}                            </div>
                            <div className="flex justify-end">
                              <button type="button" onClick={() => handleSubmitEvidence(task.id, okr.id, task.evidence_hint, evidenceValues[idx] || selectedFile)} className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-2 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-700 transition-all duration-300">Submit</button>
                            </div>
                          </form>
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="backdrop-blur-sm bg-white/5 rounded-2xl p-12 border border-dashed border-white/30">
                  <svg className="w-16 h-16 text-white/40 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002 2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <p className="text-white/60 text-xl font-light">No micro tasks found</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OkrDetails;