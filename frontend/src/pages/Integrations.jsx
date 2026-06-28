/**
 * pages/Integrations.jsx
 *
 * Fixes:
 * - M6:  All alert() calls replaced with inline toast notifications (no blocking dialogs)
 * - M5:  discord_webhook field changed to a boolean (backend now returns is_discord_connected)
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Mail, CheckCircle, MessageSquare, Zap, Power, X, Check, AlertTriangle,
} from 'lucide-react';
import {
  getUserSettings, getGoogleConnectUrl, saveDiscordWebhook, updateUserSettings,
} from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

// ── Inline Toast ──────────────────────────────────────────────────────────────
const Toast = ({ message, type = 'success', onDismiss }) => (
  <div className={`fixed top-5 right-5 z-[200] flex items-center gap-3 px-4 py-3 rounded-card shadow-modal text-sm font-medium animate-fade-in max-w-sm ${
    type === 'success'
      ? 'bg-success text-white'
      : 'bg-error text-white'
  }`}>
    {type === 'success' ? <Check size={16} /> : <AlertTriangle size={16} />}
    <span className="flex-1">{message}</span>
    <button onClick={onDismiss} className="opacity-70 hover:opacity-100 transition-opacity">
      <X size={14} />
    </button>
  </div>
);

const Integrations = () => {
  const [settings,           setSettings]           = useState(null);
  const [loading,            setLoading]            = useState(true);
  const [connecting,         setConnecting]         = useState(false);
  const [discordWebhook,     setDiscordWebhook]     = useState('');
  const [savingDiscord,      setSavingDiscord]      = useState(false);
  const [togglingAutomation, setTogglingAutomation] = useState(false);
  const [changingWebhook,    setChangingWebhook]    = useState(false); // show change-URL input
  const [toast,              setToast]              = useState(null); // { message, type }

  const location = useLocation();

  const showToast = useCallback((message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  }, []);

  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      const res = await getUserSettings();
      setSettings(res.data);
      // discord_webhook is now a boolean from the backend
      if (res.data?.discord_webhook) {
        setDiscordWebhook('••••••••••••••••••••••••••••••••••••••••••'); // masked display
      }
    } catch {
      showToast('Failed to load settings. Please refresh the page.', 'error');
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    const query  = new URLSearchParams(location.search);
    const status = query.get('status');
    const error  = query.get('error');

    if (status === 'success') {
      showToast('Gmail connected successfully!');
      window.history.replaceState({}, document.title, '/integrations');
    } else if (error) {
      showToast(`Failed to connect Google account: ${error.replace(/_/g, ' ')}`, 'error');
      window.history.replaceState({}, document.title, '/integrations');
    }

    fetchSettings();
  }, [location.search, fetchSettings, showToast]);

  const handleConnectGmail = async () => {
    try {
      setConnecting(true);
      const res = await getGoogleConnectUrl();
      if (res?.url) {
        window.location.href = res.url;
      } else {
        showToast('Failed to get Google connect URL.', 'error');
        setConnecting(false);
      }
    } catch {
      showToast('Failed to start Google connection. Please try again.', 'error');
      setConnecting(false);
    }
  };

  const handleSaveDiscord = async () => {
    if (!discordWebhook.startsWith('https://discord.com/api/webhooks/')) {
      showToast('Please enter a valid Discord Webhook URL.', 'error');
      return;
    }

    try {
      setSavingDiscord(true);
      await saveDiscordWebhook(discordWebhook);
      showToast('Discord webhook connected and saved!');
      setChangingWebhook(false);
      setDiscordWebhook('');
      await fetchSettings();
    } catch (err) {
      showToast(
        err.response?.data?.error || 'Failed to validate or save Discord webhook.',
        'error',
      );
    } finally {
      setSavingDiscord(false);
    }
  };

  const handleCancelChange = () => {
    setChangingWebhook(false);
    setDiscordWebhook('');
  };

  const handleToggleAutomation = async () => {
    try {
      setTogglingAutomation(true);
      const newStatus = !settings.automation_enabled;
      await updateUserSettings({ automation_enabled: newStatus });
      setSettings((prev) => ({ ...prev, automation_enabled: newStatus }));
      showToast(newStatus ? 'Automation enabled!' : 'Automation paused.');
    } catch {
      showToast('Failed to update automation settings. Please try again.', 'error');
    } finally {
      setTogglingAutomation(false);
    }
  };

  if (loading && !settings) {
    return <div className="h-full flex items-center justify-center"><LoadingSpinner text="Loading Integrations..." /></div>;
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Inline Toast — M6: replaces all alert() calls */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onDismiss={() => setToast(null)}
        />
      )}

      <div>
        <h1 className="text-2xl md:text-[32px] font-bold text-heading leading-tight">Integrations &amp; Settings</h1>
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
                  <span className="font-semibold text-primary">Beta Access:</span>{' '}
                  If you aren't on the approved test list, connecting will fail.
                  <a
                    href="mailto:nitishsaini044@gmail.com?subject=SynapseSync%20Beta%20Access%20Request&body=Please%20enter%20the%20email%20address%20you%20want%20to%20connect%3A%20"
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
                <p className="text-muted text-sm mt-1">Receive instant AI lead notifications in your Discord server.</p>
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
            {/* ── Already connected — show change button unless editing ── */}
            {settings?.discord_webhook && !changingWebhook ? (
              <div className="flex flex-col gap-3">
                <div className="flex items-center gap-2 text-sm text-muted bg-success/5 border border-success/20 rounded-xl px-4 py-3">
                  <CheckCircle size={15} className="text-success shrink-0" />
                  <span>Webhook connected and encrypted securely.</span>
                </div>
                <button
                  id="change-discord-webhook-btn"
                  onClick={() => { setChangingWebhook(true); setDiscordWebhook(''); }}
                  className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl font-medium text-sm border border-[#5865F2]/40 text-[#5865F2] hover:bg-[#5865F2]/10 transition-all duration-200"
                >
                  <MessageSquare size={16} />
                  Change Webhook URL
                </button>
              </div>
            ) : (
              /* ── New connection OR editing existing ── */
              <div className="flex flex-col gap-3">
                <label className="block text-sm font-medium text-heading">
                  {settings?.discord_webhook ? 'New Webhook URL' : 'Webhook URL'}
                </label>
                <div className="flex gap-2 flex-col sm:flex-row">
                  <input
                    id="discord-webhook-input"
                    type="text"
                    placeholder="https://discord.com/api/webhooks/..."
                    className="input-field flex-1"
                    value={discordWebhook}
                    onChange={(e) => setDiscordWebhook(e.target.value)}
                    autoFocus
                  />
                  <div className="flex gap-2 sm:flex-col md:flex-row">
                    <button
                      id="save-discord-webhook-btn"
                      onClick={handleSaveDiscord}
                      disabled={savingDiscord || !discordWebhook}
                      className="btn-primary flex-1 sm:flex-none whitespace-nowrap"
                    >
                      {savingDiscord ? 'Saving...' : 'Save'}
                    </button>
                    {settings?.discord_webhook && (
                      <button
                        id="cancel-discord-webhook-btn"
                        onClick={handleCancelChange}
                        disabled={savingDiscord}
                        className="flex-1 sm:flex-none px-4 py-2 rounded-xl border border-border text-muted hover:text-heading hover:border-heading/30 transition-all text-sm font-medium"
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-xs text-muted">
                  {settings?.discord_webhook
                    ? 'Paste your new Discord webhook URL. The old one will be replaced.'
                    : 'Go to Discord → Channel Settings → Integrations → Webhooks to get your URL.'}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Automation Card */}
        <div className="bg-surface-card border border-border rounded-card p-6 shadow-card flex flex-col relative overflow-hidden">
          {settings?.automation_enabled && (
            <div className="absolute top-0 right-0 -mr-12 -mt-12 w-48 h-48 bg-primary/10 rounded-full blur-3xl pointer-events-none" />
          )}

          <div className="flex items-start justify-between relative z-10">
            <div className="flex items-center gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${settings?.automation_enabled ? 'bg-primary/10 text-primary' : 'bg-gray-100 text-gray-400'}`}>
                <Zap size={24} className={settings?.automation_enabled ? 'animate-pulse' : ''} />
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
