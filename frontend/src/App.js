import React, { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [brandInput, setBrandInput] = useState('')
  const [brandData, setBrandData] = useState(null)
  const [competitorData, setCompetitorData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [hasError, setHasError] = useState(false)

  const handleAnalyzeClick = async () => {
    if (!brandInput.trim()) {
      alert('Please enter a brand name first')
      return
    }

    setIsLoading(true)
    setHasError(false)
    setCompetitorData(null)

    try {
      console.log('Analyzing brand:', brandInput)

      // Get brand analysis
      const brandResult = await axios.post(
        'http://localhost:5000/api/analyze',
        {
          brand: brandInput,
        }
      )

      // Get competitor analysis
      const competitorResult = await axios.post(
        'http://localhost:5000/api/competitors',
        {
          brand: brandInput,
        }
      )

      setBrandData(brandResult.data)
      setCompetitorData(competitorResult.data)
    } catch (error) {
      console.log('Request failed:', error)
      setHasError(true)
      alert(
        'Could not connect to the server. Make sure the backend is running on port 5000!'
      )
    }

    setIsLoading(false)
  }

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleAnalyzeClick()
    }
  }

  const getColorForSentiment = (type) => {
    if (type === 'positive') return '#22c55e'
    if (type === 'negative') return '#ef4444'
    return '#6b7280'
  }

  const calculateRiskLevel = () => {
    if (!brandData || !brandData.mentions) return 'low'

    const negativeMentions = brandData.mentions.filter(
      (m) => m.sentiment === 'negative'
    ).length
    const totalMentions = brandData.mentions.length
    const negativePercentage = (negativeMentions / totalMentions) * 100

    if (negativePercentage > 30) return 'high'
    if (negativePercentage > 15) return 'medium'
    return 'low'
  }

  const getColorForRisk = (level) => {
    if (level === 'high') return '#ef4444'
    if (level === 'medium') return '#f59e0b'
    return '#22c55e'
  }

  const getRiskIcon = (level) => {
    if (level === 'high') return '🔴'
    if (level === 'medium') return '🟡'
    return '🟢'
  }

  const calculateSentimentScore = () => {
    if (!brandData || !brandData.mentions) return 0

    const positiveMentions = brandData.mentions.filter(
      (m) => m.sentiment === 'positive'
    ).length
    const totalMentions = brandData.mentions.length

    return totalMentions > 0
      ? Math.round((positiveMentions / totalMentions) * 100)
      : 0
  }

  const calculateRiskScore = () => {
    if (!brandData || !brandData.mentions) return 0

    const negativeMentions = brandData.mentions.filter(
      (m) => m.sentiment === 'negative'
    ).length
    const totalMentions = brandData.mentions.length
    const negativePercentage = (negativeMentions / totalMentions) * 100

    return Math.min(100, Math.round(negativePercentage * 2))
  }

  const getTotalMentions = () => {
    return brandData?.mentions?.length || 0
  }

  const getMentions = () => {
    return brandData?.mentions || []
  }

  const getBrandName = () => {
    return brandData?.brand || 'Unknown Brand'
  }

  if (isLoading) {
    return (
      <div className="app">
        <header className="header">
          <h1>🌐 Echosphere</h1>
          <p>Listening to your brand's digital heartbeat</p>
        </header>

        <div className="loading-section">
          <div className="loading-spinner"></div>
          <p>Scanning the web for {brandInput} mentions...</p>
          <p className="loading-subtitle">
            Analyzing competitors and market position
          </p>
        </div>
      </div>
    )
  }

  if (hasError) {
    return (
      <div className="app">
        <header className="header">
          <h1>🌐 Echosphere</h1>
          <p>Listening to your brand's digital heartbeat</p>
        </header>

        <div className="error-section">
          <div className="error-icon">⚠️</div>
          <h2>Connection Issue</h2>
          <p>Couldn't reach the analysis server.</p>
          <p>Make sure the backend is running on port 5000.</p>
          <button onClick={() => setHasError(false)} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  const riskLevel = calculateRiskLevel()
  const sentimentScore = calculateSentimentScore()
  const riskScore = calculateRiskScore()

  return (
    <div className="app">
      <header className="header">
        <h1>🌐 Echosphere</h1>
        <p>Listening to your brand's digital heartbeat</p>
      </header>

      <section className="search-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Try: Nike, Starbucks, Apple..."
            value={brandInput}
            onChange={(e) => setBrandInput(e.target.value)}
            onKeyPress={handleKeyPress}
            className="brand-input"
          />
          <button onClick={handleAnalyzeClick} className="analyze-button">
            Analyze Brand
          </button>
        </div>
      </section>

      {brandData ? (
        <main className="results-section">
          {/* Summary cards */}
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Total Mentions</h3>
              <div className="metric-value">{getTotalMentions()}</div>
              <p>Across all platforms</p>
            </div>

            <div className="metric-card">
              <h3>Sentiment Score</h3>
              <div
                className="metric-value"
                style={{ color: getColorForSentiment('positive') }}
              >
                {sentimentScore}%
              </div>
              <p>Positive mentions</p>
            </div>

            <div className="metric-card">
              <h3>Risk Level</h3>
              <div
                className="metric-value"
                style={{ color: getColorForRisk(riskLevel) }}
              >
                {getRiskIcon(riskLevel)} {riskLevel}
              </div>
              <p>Current brand health</p>
            </div>

            <div className="metric-card">
              <h3>Risk Score</h3>
              <div className="metric-value">{riskScore}/100</div>
              <p>Lower is better</p>
            </div>
          </div>

          {/* Crisis Alerts */}
          {riskLevel === 'high' && (
            <div className="warning-banner">
              <span className="warning-icon">🚨</span>
              <div className="warning-text">
                <strong>High Alert:</strong> We're detecting significant
                negative sentiment. You might want to address this quickly.
              </div>
            </div>
          )}

          {riskLevel === 'medium' && (
            <div className="warning-banner medium">
              <span className="warning-icon">⚠️</span>
              <div className="warning-text">
                <strong>Medium Alert:</strong> Some negative sentiment detected.
                Keep an eye on this.
              </div>
            </div>
          )}

          {/* Competitor Comparison */}
          {competitorData && (
            <section className="competitor-section">
              <h2>How {getBrandName()} Stacks Up Against Competitors</h2>

              <div className="competitor-grid">
                <div className="competitor-card main-brand">
                  <h3>{competitorData.main_brand.name}</h3>
                  <div className="competitor-metric">
                    <span className="metric-label">Mentions:</span>
                    <span className="metric-value">
                      {competitorData.main_brand.mentions}
                    </span>
                  </div>
                  <div className="competitor-metric">
                    <span className="metric-label">Sentiment:</span>
                    <span
                      className="metric-value"
                      style={{ color: getColorForSentiment('positive') }}
                    >
                      {competitorData.main_brand.sentiment_score}%
                    </span>
                  </div>
                  <div className="performance-badge">Your Brand</div>
                </div>

                {competitorData.competitors.map((competitor, index) => (
                  <div key={index} className="competitor-card">
                    <h3>{competitor.name}</h3>
                    <div className="competitor-metric">
                      <span className="metric-label">Mentions:</span>
                      <span className="metric-value">
                        {competitor.mentions}
                      </span>
                    </div>
                    <div className="competitor-metric">
                      <span className="metric-label">Sentiment:</span>
                      <span
                        className="metric-value"
                        style={{ color: getColorForSentiment('positive') }}
                      >
                        {competitor.sentiment_score}%
                      </span>
                    </div>
                    <div className="trend-indicator">
                      {competitor.sentiment_score >
                      competitorData.main_brand.sentiment_score
                        ? '📈'
                        : '📉'}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Mentions list */}
          <section className="mentions-section">
            <h2>What People Are Saying About {getBrandName()}</h2>

            <div className="mentions-list">
              {getMentions().map((mention) => (
                <div key={mention.id} className="mention-item">
                  <div className="mention-header">
                    <span className="platform">
                      {mention.platform === 'Twitter' && '🐦'}
                      {mention.platform === 'Instagram' && '📸'}
                      {mention.platform === 'Reddit' && '👥'}
                      {mention.platform === 'News' && '📰'}
                      {mention.platform === 'Forum' && '💬'}
                      {mention.platform === 'Blog' && '📝'}
                      {mention.platform || 'Social'}
                    </span>

                    <span
                      className="sentiment-tag"
                      style={{
                        backgroundColor: getColorForSentiment(
                          mention.sentiment
                        ),
                        color: 'white',
                      }}
                    >
                      {mention.sentiment || 'neutral'}
                    </span>
                  </div>

                  <p className="mention-content">
                    {mention.text || 'No content available'}
                  </p>

                  <div className="mention-footer">
                    <span className="user">
                      👤 {mention.username || 'anonymous'}
                    </span>
                    <span className="engagement">
                      ❤️ {mention.engagement || 0} likes
                    </span>
                    <span className="mood">
                      {mention.emotion === 'anger' && '😠'}
                      {mention.emotion === 'excitement' && '🎉'}
                      {mention.emotion === 'joy' && '😊'}
                      {mention.emotion === 'frustration' && '😤'}
                      {mention.emotion === 'surprise' && '😲'}
                      {mention.emotion || '😐'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </main>
      ) : (
        <section className="features-section">
          <h2>See Your Brand Through Our Eyes</h2>
          <p className="features-intro">
            Echosphere helps you understand what the internet is saying about
            your brand. We scan social media, news sites, and forums to give you
            the full picture.
          </p>

          <div className="features-grid">
            <div className="feature">
              <div className="feature-icon">🔍</div>
              <h3>Find Every Mention</h3>
              <p>We search everywhere people talk about brands</p>
            </div>

            <div className="feature">
              <div className="feature-icon">😊</div>
              <h3>Understand Feelings</h3>
              <p>See if people are happy, angry, or just talking</p>
            </div>

            <div className="feature">
              <div className="feature-icon">🚨</div>
              <h3>Spot Problems Early</h3>
              <p>Get alerts before small issues become big ones</p>
            </div>

            <div className="feature">
              <div className="feature-icon">⚔️</div>
              <h3>Beat Competitors</h3>
              <p>See how you stack up against the competition</p>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}

export default App
