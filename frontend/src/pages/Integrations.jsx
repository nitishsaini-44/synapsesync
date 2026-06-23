import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Mail, CheckCircle, Settings as SettingsIcon, MessageSquare, Zap, Power } from 'lucide-react';
import { getUserSettings, getGoogleConnectUrl, saveDiscordWebhook, updateUserSettings } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

const Integrations = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [discordWebhook, setDiscordWebhook] = useState('');
  const [savingDiscord, setSavingDiscord] = useState(false);
  const [togglingAutomation, setTogglingAutomation] = useState(false);
  
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Check if we just returned from Google OAuth redirect
    const query = new URLSearchParams(location.search);
    const status = query.get('status');
    const error = query.get('error');
    
    if (status === 'success') {
      alert("Gmail connected successfully!");
      window.history.replaceState({}, document.title, '/integrations');
    } else if (error) {
      alert(`Failed to connect Google account: ${error}`);
      window.history.replaceState({}, document.title, '/integrations');
    }
    
    fetchSettings();
  }, [location]);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const res = await getUserSettings();
      setSettings(res.data);
      if (res.data.discord_webhook) {
        setDiscordWebhook('••••••••••••••••••••••••••••••••••••••••••'); // Masked for security
      }
    } catch (error) {
      console.error("Failed to load settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectGmail = async () => {
    try {
      setConnecting(true);
      const res = await getGoogleConnectUrl();
      if (res.url) {
        window.location.href = res.url;
      }
    } catch (error) {
      console.error("Failed to get connect URL:", error);
      alert("Failed to start Google connection.");
      setConnecting(false);
    }
  };

  const handleSaveDiscord = async () => {
    if (!discordWebhook.startsWith('https://discord.com/api/webhooks/')) {
      alert("Please enter a valid Discord Webhook URL starting with https://discord.com/api/webhooks/");
      return;
    }
    
    try {
      setSavingDiscord(true);
      await saveDiscordWebhook(discordWebhook);
      alert("Discord webhook connected and saved successfully!");
      await fetchSettings();
    } catch (error) {
      console.error("Failed to save discord webhook:", error);
      alert(error.response?.data?.error || "Failed to validate or save Discord Webhook. Please check the URL.");
    } finally {
      setSavingDiscord(false);
    }
  };

  const handleToggleAutomation = async () => {
    try {
      setTogglingAutomation(true);
      const newStatus = !settings.automation_enabled;
      await updateUserSettings({ automation_enabled: newStatus });
      setSettings(prev => ({ ...prev, automation_enabled: newStatus }));
    } catch (error) {
      console.error("Failed to toggle automation:", error);
      alert("Failed to update automation settings. Please try again.");
    } finally {
      setTogglingAutomation(false);
    }
  };

  if (loading && !settings) {
    return <div className="h-full flex items-center justify-center"><LoadingSpinner text="Loading Integrations..." /></div>;
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl md:text-[32px] font-bold text-heading leading-tight">Integrations & Settings</h1>
        <p className="text-sm md:text-[15px] text-muted mt-1">Connect your accounts and enable automated workflows.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Gmail Integration Card */}
        <div className="bg-surface-card border border-border rounded-card p-6 shadow-card flex flex-col">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-red-500/10 rounded-full flex items-center justify-center text-red-500">
                <Mail size={24} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-heading">Google Gmail</h3>
                <p className="text-muted text-sm mt-1">Connect your Gmail to allow SynapseSync to read your emails.</p>
              </div>
            </div>
            
            {settings?.is_gmail_connected ? (
              <div className="flex items-center gap-2 text-success bg-success/10 px-3 py-1.5 rounded-full text-sm font-medium">
                <CheckCircle size={16} />
                Connected
              </div>
            ) : null}
          </div>

          <div className="mt-6 pt-6 border-t border-border mt-auto">
            {settings?.is_gmail_connected ? (
              <div>
                <p className="text-sm text-muted mb-2">Connected Account:</p>
                <p className="font-medium text-heading">{settings.google_email}</p>
                <button 
                  onClick={handleConnectGmail} 
                  disabled={connecting}
                  className="mt-4 text-sm text-primary hover:text-primary-hover font-medium transition-colors"
                >
                  {connecting ? 'Connecting...' : 'Reconnect Account'}
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-3">
                <button
                  onClick={handleConnectGmail}
                  disabled={connecting}
                  className="btn-primary w-full"
                >
                  {connecting ? 'Connecting...' : 'Connect Gmail Account'}
                </button>
                <div className="bg-primary/5 rounded-lg p-3 text-xs text-muted border border-primary/10">
                  <span className="font-semibold text-primary">Beta Access:</span> If you aren't on the approved test list, connecting will fail.
                  <a 
                    href="https://mail.google.com/mail/?view=cm&fs=1&to=nitishsaini044@gmail.com&su=SynapseSync%20Beta%20Access%20Request&body=Hello%20Nitish%2C%0A%0AI%20would%20like%20to%20request%20beta%20access%20to%20the%20SynapseSync%20platform.%0APlease%20add%20the%20following%20email%20address%20to%20the%20approved%20Google%20Test%20Users%20list%20so%20I%20can%20connect%20my%20Gmail%20account%3A%0A%0A%5BEnter%20your%20email%20address%20here%5D%0A%0AThank%20you!" 
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block mt-1.5 text-primary hover:underline font-medium"
                  >
                    Request access via email &rarr;
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Discord Integration Card */}
        <div className="bg-surface-card border border-border rounded-card p-6 shadow-card flex flex-col">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-[#5865F2]/10 rounded-full flex items-center justify-center text-[#5865F2]">
                <MessageSquare size={24} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-heading">Discord Webhook</h3>
                <p className="text-muted text-sm mt-1">Receive instant AI lead notifications directly in your Discord server.</p>
              </div>
            </div>
            
            {settings?.discord_webhook ? (
              <div className="flex items-center gap-2 text-success bg-success/10 px-3 py-1.5 rounded-full text-sm font-medium">
                <CheckCircle size={16} />
                Connected
              </div>
            ) : null}
          </div>

          <div className="mt-6 pt-6 border-t border-border mt-auto">
            <label className="block text-sm font-medium text-heading mb-2">Webhook URL</label>
            <div className="flex gap-3 flex-col sm:flex-row">
              <input 
                type="text" 
                placeholder="https://discord.com/api/webhooks/..." 
                className="input-field flex-1"
                value={discordWebhook}
                onChange={(e) => setDiscordWebhook(e.target.value)}
              />
              <button 
                onClick={handleSaveDiscord}
                disabled={savingDiscord || !discordWebhook}
                className="btn-primary sm:w-auto"
              >
                {savingDiscord ? 'Saving...' : 'Save'}
              </button>
            </div>
            {settings?.discord_webhook && (
              <p className="text-xs text-muted mt-3">
                Your webhook is securely encrypted. Paste a new one to update.
              </p>
            )}
          </div>
        </div>

        {/* Automation Card */}
        <div className="bg-surface-card border border-border rounded-card p-6 shadow-card flex flex-col relative overflow-hidden">
          {/* Subtle background glow when active */}
          {settings?.automation_enabled && (
            <div className="absolute top-0 right-0 -mr-12 -mt-12 w-48 h-48 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>
          )}
          
          <div className="flex items-start justify-between relative z-10">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${settings?.automation_enabled ? 'bg-primary/10 text-primary' : 'bg-gray-100 text-gray-400'}`}>
                <Zap size={24} className={settings?.automation_enabled ? "animate-pulse" : ""} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-heading">Engine Status</h3>
                <p className="text-muted text-sm mt-1">Enable or disable background email scanning and AI classification.</p>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-border mt-auto relative z-10">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium text-heading">Current Status:</span>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${settings?.automation_enabled ? 'bg-success/10 text-success' : 'bg-gray-100 text-gray-500'}`}>
                {settings?.automation_enabled ? 'Active' : 'Paused'}
              </span>
            </div>
            
            <button
              onClick={handleToggleAutomation}
              disabled={togglingAutomation || !settings?.is_gmail_connected}
              className={`w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl font-medium transition-all duration-200 ${
                settings?.automation_enabled 
                  ? 'bg-error/10 text-error hover:bg-error/20' 
                  : 'bg-primary text-white hover:bg-primary-hover shadow-md hover:shadow-lg'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <Power size={18} />
              {togglingAutomation 
                ? 'Updating...' 
                : (settings?.automation_enabled ? 'Pause Automation' : 'Enable Automation')
              }
            </button>
            
            {!settings?.is_gmail_connected && (
              <p className="text-xs text-error mt-3 text-center">
                You must connect Gmail before enabling automation.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Integrations;
